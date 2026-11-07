import io
from datetime import date
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from .models import Municipality, Contact, Opportunity, DirectorPlan, Signal, InternalPlan, CollectionJob, Royalty, Snapshot
from .commercial import FRENTE1_TARGETS, seed_frente1
from .prospect import seed_prospect, build_messages, collect_anp_series

PB = [('2507507', 'João Pessoa'), ('2503209', 'Cabedelo'), ('2513703', 'Santa Rita'), ('2508604', 'Lucena')]


class ProspectTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user('tester', password='test-only-password')
        self.client.force_login(self.user)
        for i, (uf, name, *_r) in enumerate(FRENTE1_TARGETS):
            Municipality.objects.create(code=f'99{i:05d}', name=name, uf=uf, source_url='https://example.org')
        for code, name in PB:
            Municipality.objects.create(code=code, name=name, uf='PB', source_url='https://example.org')

    def test_seed_idempotent_and_contacts_unverified(self):
        seed_frente1()
        first = seed_prospect()
        self.assertGreater(first['contatos'], 10)
        self.assertEqual(first['planos'], 4)
        self.assertEqual(first['oportunidades'], 4)
        self.assertEqual(first['cursos'], 2)
        self.assertEqual(seed_prospect(), {'contatos': 0, 'planos': 0, 'sinais': 0, 'oportunidades': 0, 'cursos': 0})
        self.assertFalse(Contact.objects.filter(verified_on__isnull=False).exists())
        self.assertTrue(DirectorPlan.objects.get(municipality__name='Cabedelo').confirmed)
        self.assertEqual(DirectorPlan.objects.get(municipality__name='Lucena').review_status, 'Data a conferir')
        self.assertEqual(Signal.objects.get(external_key='pesquisa:pb:lucena:plano-diretor-2001').status, 'convertido')

    def test_verify_contact_counts_as_qualified(self):
        seed_frente1(); seed_prospect()
        c = Contact.objects.get(name='Hermann Marinho Paiva')
        r = self.client.post(f'/contatos/{c.pk}/conferir/', {'next': '/metas/', 'note': 'Confirmado por telefone'})
        self.assertEqual(r.status_code, 302)
        c.refresh_from_db(); self.assertIsNotNone(c.verified_on); self.assertIn('Confirmado', c.notes)
        self.assertIn('>1</b> / 120', self.client.get('/metas/').content.decode())

    def test_messages_and_pages(self):
        seed_frente1(); seed_prospect()
        mun = Municipality.objects.get(name='Guamaré')
        job = CollectionJob.objects.create(source='anp')
        snap = Snapshot.objects.create(job=job, url='https://example.org', filename='f', sha256='a' * 64, size=1)
        Royalty.objects.create(municipality=mun, year=2024, month=1, minimum=1_000_000, excess=3_000_000, total=4_000_000, source_url='https://x.org', snapshot=snap)
        o = Opportunity.objects.get(title='Royalties — Guamaré/RN')
        m = build_messages(o)
        self.assertIn('R$ 4,0 milhões', m['body']); self.assertIn('75%', m['body'])
        self.assertIn('pgm_pg@guamare.rn.gov.br', m['to']); self.assertIn('Hermann', m['body'])
        for word in ('ortogonal', 'mapa', 'traçado'):
            self.assertNotIn(word, m['body'].lower())
        tibau = build_messages(Opportunity.objects.get(title='Royalties — Tibau/RN'))
        self.assertTrue(tibau['warnings'])
        lucena = build_messages(Opportunity.objects.get(title__startswith='Lucena'))
        self.assertIn('Plano Diretor de Lucena', lucena['body'])
        for url in ['/lista-quente/paraiba/', f'/oportunidade/{o.pk}/mensagem/', f'/oportunidade/{o.pk}/', '/ajuda/', '/royalties/', '/planos/', '/fontes/']:
            self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_series_collects_each_year_and_reports_failures(self):
        job = CollectionJob.objects.create(source='anp_serie', parameters={'first_year': 2021, 'last_year': 2023})
        def fake(j):
            if j.parameters['year'] == 2022: raise ValueError('leiaute')
            return f"{j.parameters['year']}: ok", False
        with patch('core.collectors.collect_anp', side_effect=fake):
            summary, partial = collect_anp_series(job)
        self.assertTrue(partial); self.assertIn('2021: ok', summary); self.assertIn('2022: FALHOU', summary); self.assertIn('2023: ok', summary)


class ImportFolderTests(TestCase):
    def setUp(self):
        Municipality.objects.create(code='2407203', name='Macau', uf='RN', source_url='https://example.org')

    def test_folder_imports_once_and_ytd(self):
        import tempfile
        from pathlib import Path
        from django.test import override_settings
        from core.importer import import_folder, royalty_ytd
        with tempfile.TemporaryDirectory() as tmp, override_settings(DATA_DIR=Path(tmp)):
            (Path(tmp) / 'importar').mkdir()
            (Path(tmp) / 'importar' / 'royalties-tabelas-jan-dez-2026_03.xlsx').write_bytes(b'x')
            (Path(tmp) / 'importar' / 'outro.txt').write_bytes(b'y')
            def fake(raw, year, mapping, alias_audit=None):
                m = Municipality.objects.get(name='Macau')
                return [{'municipality_id': m.pk, 'year': year, 'month': 1, 'minimum': 1, 'excess': 30, 'total': 31}], [1], []
            with patch('core.collectors.parse_anp_xlsx', side_effect=fake):
                first = import_folder(); second = import_folder()
            self.assertEqual(len(first), 1); self.assertIn('Concluída', first[0]); self.assertEqual(second, [])
            job = CollectionJob.objects.get(source='anp')
            snap = Snapshot.objects.create(job=job, url='https://x.org', filename='f', sha256='b' * 64, size=1)
            Royalty.objects.create(municipality_id='2407203', year=2025, month=1, minimum=1, excess=20, total=21, source_url='https://x.org', snapshot=snap)
            label, data = royalty_ytd(['2407203'])
            self.assertIn('2026', label); self.assertEqual(round(data['2407203']['pct']), 50)
