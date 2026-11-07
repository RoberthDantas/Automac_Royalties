import io
import tempfile
import zipfile
from datetime import timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from .models import Municipality, Opportunity, Organization, Activity, Signal, CollectionJob, Well, Snapshot
from .collectors import excluded_terms, pncp_signal
from .commercial import FRENTE1_TARGETS, seed_frente1


class CommercialTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user('tester', password='test-only-password')
        self.client.force_login(self.user)
        for i, (uf, name, *_rest) in enumerate(FRENTE1_TARGETS):
            Municipality.objects.create(code=f'99{i:05d}', name=name, uf=uf, source_url='https://example.org')

    def test_seed_is_idempotent_and_preserves_edits(self):
        self.assertEqual(seed_frente1(), len(FRENTE1_TARGETS))
        o = Opportunity.objects.get(title='Royalties — Macau/RN')
        self.assertIn('26,2', o.problem)
        o.next_action = 'Editado por mim'; o.save()
        self.assertEqual(seed_frente1(), 0)
        o.refresh_from_db(); self.assertEqual(o.next_action, 'Editado por mim')
        self.assertEqual(Organization.objects.filter(kind='prefeitura').count(), len(FRENTE1_TARGETS))

    def test_followup_cadence_and_pages(self):
        seed_frente1()
        o = Opportunity.objects.get(title='Royalties — Guamaré/RN')
        self.client.post(f'/oportunidade/{o.pk}/historico/', {'kind': 'contato', 'text': 'Ligação'})
        o.refresh_from_db()
        self.assertEqual(o.stage, 'contato')
        self.assertEqual(o.next_date, timezone.localdate() + timedelta(days=4))
        self.client.post(f'/oportunidade/{o.pk}/historico/', {'kind': 'contato', 'text': 'E-mail'})
        o.refresh_from_db(); self.assertEqual(o.next_date, timezone.localdate() + timedelta(days=10))
        self.client.post(f'/oportunidade/{o.pk}/historico/', {'kind': 'proposta', 'text': 'Proposta enviada'})
        o.refresh_from_db(); self.assertEqual(o.stage, 'proposta')
        self.assertTrue(Activity.objects.filter(opportunity=o, kind='sistema', text__startswith='Cadência').exists())
        for url in ['/lista-quente/', '/metas/', '/metas/relatorio.md', '/', '/pocos/planilha.xlsx', '/acompanhamento/']:
            self.assertEqual(self.client.get(url).status_code, 200, url)
        report = self.client.get('/metas/relatorio.md?de=2026-09-01&ate=2030-12-31').content.decode()
        self.assertIn('Proposta enviada', report)
        self.assertIn('| Propostas enviadas | 1 | 15 |', report)
        self.client.logout()
        self.assertEqual(self.client.get('/metas/').status_code, 302)

    def test_exclusion_filter_and_triage_command(self):
        self.assertTrue(excluded_terms('Aquisição de equipamentos e instrumentos topográficos e geodésicos'))
        self.assertTrue(excluded_terms('Locação de Software para gestão da Frota com georreferenciamento'))
        self.assertTrue(excluded_terms('aquisição de aparelho de georradar (GPR)'))
        self.assertFalse(excluded_terms('Contratação de empresa para levantamento topográfico e georreferenciamento'))
        self.assertFalse(excluded_terms('Serviços de aerofotogrametria e cadastro multifinalitário'))
        job = CollectionJob.objects.create(source='pncp_capacidades')
        item = {'objetoCompra': 'Aquisição de equipamentos topográficos', 'numeroControlePNCP': 'x-1'}
        self.assertFalse(pncp_signal(item, job, 'topográficos'))
        Signal.objects.create(title='Aquisição de equipamentos topográficos', kind='edital', external_key='pncp:old', source_type='pncp',
                              source_url='https://example.org', reason='r', payload={'objeto': 'Aquisição de equipamentos topográficos'})
        call_command('configurar_comercial', stdout=io.StringIO())
        s = Signal.objects.get(external_key='pncp:old')
        self.assertEqual(s.status, 'descartado'); self.assertIn('Triagem automática', s.review_note)

    def test_uncompressed_body_stored_once(self):
        from .collectors import fetch
        class Response:
            status = 200; headers = {'Content-Type': 'application/json'}
            def geturl(self): return 'https://pncp.gov.br/example'
            def read(self, n): return b'{"data":[]}'
            def __enter__(self): return self
            def __exit__(self, *args): pass
        j = CollectionJob.objects.create(source='test')
        with tempfile.TemporaryDirectory() as tmp, self.settings(DATA_DIR=Path(tmp)), patch('core.collectors.validate_remote'), \
                patch('core.collectors.urllib.request.build_opener') as mock:
            mock.return_value.open.return_value = Response()
            raw, snap = fetch('https://pncp.gov.br/example', j, 'json', attempts=1)
            files = list((Path(tmp) / 'fontes' / str(j.pk)).iterdir())
            self.assertEqual(len(files), 1)
            self.assertEqual(snap.filename, snap.provenance['received_body_file'])

    def test_anp_zip_with_several_spreadsheets(self):
        from . import collectors
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w') as z:
            z.writestr('estados_2025.xlsx', b'estados'); z.writestr('municipios_2025.xlsx', b'municipios')
            z.writestr('educacao_2025.xlsx', b'edu')
        page = b'<div id="content-core"><a href="/anp/tabelas-contendo-o-valor-mensal-dos-royalties-dos-beneficiarios/2025-1/beneficiarios_2025.zip">2025</a></div>'
        m = Municipality.objects.get(name='Macau')
        def fake_fetch(url, job, ext, **kw):
            snap = Snapshot.objects.create(job=job, url=url, filename='f', sha256='a' * 64, size=1)
            return (page if ext == 'html' else buf.getvalue()), snap
        def fake_parse(raw, year, mapping, alias_audit=None):
            if raw != b'municipios': raise ValueError('Colunas ANP não reconhecidas.')
            return [{'municipality_id': m.pk, 'year': year, 'month': 1, 'minimum': 1, 'excess': 2, 'total': 3}], [1], []
        job = CollectionJob.objects.create(source='anp', parameters={'year': 2025})
        with patch.object(collectors, 'fetch', side_effect=fake_fetch), patch.object(collectors, 'parse_anp_xlsx', side_effect=fake_parse):
            summary, partial = collectors.collect_anp(job)
        self.assertIn('municipios_2025.xlsx', summary); self.assertFalse(partial)
        self.assertEqual(m.royalty_set.get(year=2025, month=1).excess, 2)
