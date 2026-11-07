"""0.6.0: metas por trimestre, exclusão com confirmação, tela de usuários, TLS de compatibilidade e termos de editais."""
import json, ssl, urllib.error
from datetime import timedelta
from unittest.mock import patch, MagicMock
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from .models import (Activity, Attachment, CashEntry, CollectionJob, Contact, Opportunity, Organization, Signal)
from .commercial import quarter_metrics, quarter_bounds
from .bid_scans import CAPABILITIES
from .collectors import matched_terms, excluded_terms, fetch

User = get_user_model()


class Base(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser('adm', '', 'senha-de-teste-123', first_name='Ana')
        self.client.force_login(self.user)
        self.org = Organization.objects.create(name='Prefeitura Y', kind='prefeitura')


class QuarterMetricsTests(Base):
    def metric(self, label, today=None):
        return next(r['value'] for r in quarter_metrics(today)['rows'] if r['label'].startswith(label))

    def test_stage_change_is_stamped_and_scoped(self):
        o = Opportunity.objects.create(title='A', organization=self.org, front='royalties', next_action='x')
        first = o.stage_changed_at
        self.assertIsNotNone(first)
        o.next_action = 'y'; o.save()
        self.assertEqual(Opportunity.objects.get(pk=o.pk).stage_changed_at, first)
        o.stage = 'contratada'; o.save()
        self.assertEqual(self.metric('Contratos'), 1)
        q_start, _ = quarter_bounds(timezone.localdate())
        Opportunity.objects.filter(pk=o.pk).update(stage_changed_at=timezone.now() - timedelta(days=200))
        self.assertEqual(self.metric('Contratos'), 0)

    def test_contacts_and_signals_count_only_this_quarter(self):
        today = timezone.localdate()
        Contact.objects.create(organization=self.org, name='Hoje', verified_on=today)
        Contact.objects.create(organization=self.org, name='Antigo', verified_on=today - timedelta(days=200))
        self.assertEqual(self.metric('Contatos qualificados'), 1)
        s = Signal.objects.create(title='Edital', kind='licitacao', external_key='k1', source_url='https://pncp.gov.br/x',
                                  reason='r', source_type='pncp')
        self.assertIsNone(s.reviewed_at)
        s.status = 'descartado'; s.save(update_fields=['status'])
        self.assertIsNotNone(Signal.objects.get(pk=s.pk).reviewed_at)
        self.assertEqual(self.metric('Editais'), 1)
        s.status = 'novo'; s.save()
        self.assertIsNone(Signal.objects.get(pk=s.pk).reviewed_at)


class DeleteTests(Base):
    def test_delete_opportunity_requires_confirmation_and_logs(self):
        o = Opportunity.objects.create(title='Apagar', organization=self.org, front='royalties', next_action='x')
        Activity.objects.create(opportunity=o, kind='nota', text='n')
        r = self.client.get(f'/oportunidades/{o.pk}/excluir/')
        self.assertContains(r, 'Excluir definitivamente')
        self.client.post(f'/oportunidades/{o.pk}/excluir/', {})
        self.assertTrue(Opportunity.objects.filter(pk=o.pk).exists())
        r = self.client.post(f'/oportunidades/{o.pk}/excluir/', {'confirmar': 'sim'})
        self.assertEqual(r['Location'], '/oportunidades/')
        self.assertFalse(Opportunity.objects.filter(pk=o.pk).exists())
        self.assertFalse(Activity.objects.filter(opportunity_id=o.pk).exists())
        last = (settings.DATA_DIR / 'logs' / 'exclusoes.jsonl').read_text(encoding='utf-8').strip().splitlines()[-1]
        entry = json.loads(last)
        self.assertEqual(entry['registro'], 'Apagar')
        self.assertTrue(any(d['model'] == 'core.activity' for d in entry['dados']))

    def test_protected_organization_is_blocked(self):
        Opportunity.objects.create(title='Liga', organization=self.org, front='royalties', next_action='x')
        r = self.client.post(f'/organizacoes/{self.org.pk}/excluir/', {'confirmar': 'sim'})
        self.assertContains(r, 'Não é possível excluir')
        self.assertTrue(Organization.objects.filter(pk=self.org.pk).exists())

    def test_delete_contact_and_unknown_entity(self):
        c = Contact.objects.create(organization=self.org, name='Fulano')
        self.assertContains(self.client.get(f'/contatos/{c.pk}/editar/'), f'/contatos/{c.pk}/excluir/')
        self.client.post(f'/contatos/{c.pk}/excluir/', {'confirmar': 'sim'})
        self.assertFalse(Contact.objects.filter(pk=c.pk).exists())
        self.assertEqual(self.client.get('/municipios/1/excluir/').status_code, 404)


class UserScreenTests(Base):
    def test_create_edit_and_guards(self):
        self.assertContains(self.client.get('/usuarios/'), 'adm')
        r = self.client.post('/usuarios/nova/', {'full_name': 'Bruno Lima', 'username': 'bruno', 'password1': 'Cartografia#2026', 'password2': 'Cartografia#2026'})
        self.assertEqual(r.status_code, 302)
        b = User.objects.get(username='bruno')
        self.assertTrue(b.is_superuser and b.check_password('Cartografia#2026'))
        self.assertEqual(b.get_full_name(), 'Bruno Lima')
        r = self.client.post('/usuarios/nova/', {'full_name': 'X', 'username': 'bruno', 'password1': 'Cartografia#2026', 'password2': 'Cartografia#2026'})
        self.assertContains(r, 'Já existe')
        r = self.client.post(f'/usuarios/{self.user.pk}/', {'full_name': 'Ana', 'is_active': ''})
        self.assertContains(r, 'própria conta')
        self.client.post(f'/usuarios/{b.pk}/', {'full_name': 'Bruno L.', 'is_active': ''})
        self.assertFalse(User.objects.get(pk=b.pk).is_active)
        self.client.post(f'/usuarios/{self.user.pk}/', {'full_name': 'Ana S', 'is_active': 'on', 'password1': 'NovaSenha#2026x', 'password2': 'NovaSenha#2026x'})
        self.assertTrue(User.objects.get(pk=self.user.pk).check_password('NovaSenha#2026x'))
        self.assertEqual(self.client.get('/usuarios/').status_code, 200)   # sessão mantida após trocar a senha


class TlsAndTermsTests(TestCase):
    def test_handshake_failure_retries_with_compat_profile(self):
        job = CollectionJob.objects.create(source='diarios')
        good = MagicMock(); good.status = 200; good.geturl.return_value = 'https://api.queridodiario.ok.org.br/x'
        good.headers = {}; good.read.return_value = b'{"gazettes":[]}'
        good.__enter__.return_value = good
        failing = MagicMock(); failing.open.side_effect = urllib.error.URLError(ssl.SSLError(1, '[SSL: SSLV3_ALERT_HANDSHAKE_FAILURE]'))
        compat = MagicMock(); compat.open.return_value = good
        with patch('core.collectors.validate_remote'), patch('core.collectors.urllib.request.build_opener', side_effect=[failing, compat]):
            raw, snap = fetch('https://api.queridodiario.ok.org.br/x', job, 'json', attempts=1)
        self.assertEqual(raw, b'{"gazettes":[]}')
        self.assertEqual(snap.provenance['tls'], 'compatibilidade')

    def test_new_terms_match_without_noise(self):
        terms = ', '.join(v['terms'] for v in CAPABILITIES.values())
        self.assertTrue(matched_terms('Estudo de Viabilidade Técnica, Ambiental e Econômica voltado ao controle da erosão', terms))
        self.assertTrue(matched_terms('Elaboração de diagnósticos socioambientais e planos de gestão ambiental', terms))
        self.assertFalse(matched_terms('Aquisição de material de limpeza e manutenção ambiental de praças', terms))


class RecoverTests(Base):
    def test_recover_deleted_opportunity(self):
        from io import StringIO
        from django.core.management import call_command
        o = Opportunity.objects.create(title='Volta', organization=self.org, front='royalties', next_action='x')
        Activity.objects.create(opportunity=o, kind='nota', text='nota antiga')
        self.client.post(f'/oportunidades/{o.pk}/excluir/', {'confirmar': 'sim'})
        out = StringIO(); call_command('recuperar_exclusao', stdout=out)
        n = len(out.getvalue().strip().splitlines()) - 1
        call_command('recuperar_exclusao', numero=n, stdout=StringIO())
        self.assertTrue(Opportunity.objects.filter(pk=o.pk, title='Volta').exists())
        self.assertTrue(Activity.objects.filter(opportunity_id=o.pk, text='nota antiga').exists())
