from datetime import date
from io import StringIO
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from .commercial import quarter_bounds, quarter_label, seed_frente1
from .models import Municipality, Organization, Opportunity
from .prospect import build_messages, seed_prospect


class EntregaTests(TestCase):
    def setUp(self):
        call_command('configurar_territorio', stdout=StringIO())

    def test_trimestre_avanca(self):
        self.assertEqual(quarter_bounds(date(2026, 10, 6)), (date(2026, 9, 1), date(2026, 11, 30)))
        self.assertEqual(quarter_bounds(date(2026, 12, 15)), (date(2026, 12, 1), date(2027, 2, 28)))
        self.assertEqual(quarter_bounds(date(2027, 3, 1)), (date(2027, 3, 1), date(2027, 5, 31)))
        self.assertEqual(quarter_label(date(2026, 12, 1), date(2027, 2, 28)), 'dez. 2026 a fev. 2027')

    def test_assinatura_pelo_usuario(self):
        seed_frente1(); seed_prospect()
        o = Opportunity.objects.get(title='Royalties — Guamaré/RN')
        sem_nome = build_messages(o)
        self.assertIn('[seu nome]', sem_nome['body']); self.assertTrue(any('nome completo' in w for w in sem_nome['warnings']))
        u = get_user_model().objects.create_user('gilberto', password='x', first_name='Gilberto', last_name='Silva')
        m = build_messages(o, u)
        self.assertIn('Sou Gilberto Silva, da Automac_Royalties', m['body']); self.assertIn('Gilberto Silva\nAutomac_Royalties', m['body'])
        self.assertIn('"Sou Gilberto, da Automac_Royalties', m['call'])
        self.assertNotIn('Uendry', m['body'] + m['call'])

    def test_comandos_de_conta(self):
        call_command('criar_usuario', nome='Gilberto de Souza', usuario='gilberto', senha='Carto-Geo-2026!', stdout=StringIO())
        u = get_user_model().objects.get(username='gilberto')
        self.assertTrue(u.is_superuser); self.assertEqual(u.get_full_name(), 'Gilberto de Souza')
        with self.assertRaises(CommandError):
            call_command('criar_usuario', nome='X', usuario='gilberto2', senha='123', stdout=StringIO())
        with self.assertRaises(CommandError):
            call_command('alterar_usuario', usuario='gilberto', desativar=True, stdout=StringIO())
        call_command('criar_usuario', nome='Conta Comercial', usuario='comercial', senha='Outra-Senha-2026!', stdout=StringIO())
        call_command('alterar_usuario', usuario='comercial', desativar=True, stdout=StringIO())
        self.assertFalse(get_user_model().objects.get(username='comercial').is_active)
        call_command('alterar_usuario', usuario='gilberto', nome='Gilberto Souza', senha='Nova-Senha-2026!', stdout=StringIO())
        u.refresh_from_db(); self.assertEqual(u.get_full_name(), 'Gilberto Souza'); self.assertTrue(u.check_password('Nova-Senha-2026!'))

    def test_telas_com_usuario_e_alvo_sem_municipio(self):
        seed_frente1(); seed_prospect()
        u = get_user_model().objects.create_user('gilberto', password='x', first_name='Gilberto')
        self.client.force_login(u)
        o = Opportunity.objects.filter(front='royalties').first()
        org = Organization.objects.create(name='Órgão sem município', kind='outro', role='comprador')
        o.organization = org; o.save()
        self.assertEqual(self.client.get('/lista-quente/').status_code, 200)
        home = self.client.get('/').content.decode()
        self.assertIn('Gilberto, reúna', home); self.assertNotIn('Uendry', home)
        goals = self.client.get('/metas/').content.decode()
        self.assertIn('Metas do trimestre', goals); self.assertIn('↓ Relatório de', goals)
        report = self.client.get('/metas/relatorio.md').content.decode()
        self.assertIn('Gerado por: Gilberto', report); self.assertNotIn('Uendry', report)
