import json
import tempfile
from datetime import datetime, date, time, timedelta
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import *
from .scheduling import next_occurrence, schedule_parameters, tick
from .intelligence import parse_feed, save_signal, collect_sources

class CentralTests(TestCase):
    def setUp(self):
        self.user=get_user_model().objects.create_user('central-test',password='only-for-tests-123')
        self.client.force_login(self.user)
        self.m=Municipality.objects.create(code='2507507',name='João Pessoa',uf='PB',source_url='https://example.org')
        self.org=Organization.objects.create(name='Cartório exemplo',kind='cartorio',cnpj='001234',municipality=self.m,address='Rua A, 10',attributes='Registro de Imóveis')
        self.c=Contact.objects.create(organization=self.org,name='Atendimento',email='valid@example.org',phone='(83) 1234-5678')
        self.s=CollectionSchedule.objects.create(name='Poços semanal',source='pocos',frequency='weekly',at_time=time(8),weekday=0,next_run=timezone.now()-timedelta(minutes=1))

    def test_calendar_local_month_end_and_leap(self):
        zone=ZoneInfo('America/Fortaleza')
        self.s.frequency='monthly';self.s.monthday=31
        self.assertEqual(next_occurrence(self.s,datetime(2026,2,1,tzinfo=zone)).date(),date(2026,2,28))
        self.assertEqual(next_occurrence(self.s,datetime(2028,2,1,tzinfo=zone)).date(),date(2028,2,29))
        self.s.frequency='weekly';self.s.weekday=0
        self.assertEqual(next_occurrence(self.s,datetime(2026,9,28,8,tzinfo=zone)).date(),date(2026,10,5))
        self.s.frequency='daily'
        self.assertEqual(next_occurrence(self.s,datetime(2026,9,28,9,tzinfo=zone)).date(),date(2026,9,29))

    def test_pages_auth_filters_and_exports(self):
        save_signal('test:reurb',{'title':'Regularização fundiária REURB','kind':'fundiaria','source_url':'https://example.org/x','reason':'Teste','source_type':'pncp','municipality':self.m})
        paths=['/','/cartorios/','/cartorios/exportar.csv','/agenda/','/agenda/nova/',f'/agenda/{self.s.pk}/','/radar/','/radar/?topic=reurb&origin=pncp&uf=PB','/cobertura/','/central/pulso/','/central/briefing.md']
        for path in paths:
            with self.subTest(path=path):self.assertEqual(self.client.get(path).status_code,200)
        self.assertContains(self.client.get('/radar/?topic=reurb'),'Regularização fundiária REURB')
        self.assertContains(self.client.get('/cartorios/'),'Rua A, 10')
        self.client.logout()
        for path in paths:self.assertEqual(self.client.get(path).status_code,302)

    def test_contact_opt_out_and_csv_formula(self):
        self.c.do_not_contact=True;self.c.email='blocked@example.org';self.c.save()
        self.org.address='  =HYPERLINK("x")';self.org.save()
        response=self.client.get('/cartorios/')
        self.assertContains(response,'0 e-mails únicos')
        response=self.client.get('/cartorios/exportar.csv')
        self.assertIn("'  =HYPERLINK",response.content.decode())
        self.assertIn('SIM',response.content.decode())

    def test_recollect_preserves_review_and_change_date(self):
        d={'title':'Plano diretor','kind':'plano','source_url':'https://example.org','reason':'Consulta','payload':{},'source_type':'pagina'}
        s,_=save_signal('test:one',d);s.status='descartado';s.review_note='Fora do recorte';s.save()
        old=s.updated_at
        s,_=save_signal('test:one',{**d,'payload':{}})
        self.assertEqual(s.status,'descartado');self.assertEqual(s.review_note,'Fora do recorte');self.assertEqual(s.updated_at,old)
        self.assertIsNotNone(s.last_seen_at)

    def test_rss_atom_and_invalid_html(self):
        xml=b'<rss><channel><item><title>Plano diretor</title><link>https://example.org/x</link><description>&lt;b&gt;reurb&lt;/b&gt;</description><pubDate>Mon, 28 Sep 2026 08:00:00 -0300</pubDate></item></channel></rss>'
        rows=parse_feed(xml,'https://example.org')
        self.assertEqual(rows[0]['body'],'reurb');self.assertEqual(rows[0]['date'],date(2026,9,28))
        atom=b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>Teste</title><link href="/artigo"/><updated>2026-09-28T11:00:00Z</updated></entry></feed>'
        self.assertEqual(parse_feed(atom,'https://example.org')[0]['url'],'https://example.org/artigo')
        with self.assertRaises(ValueError):parse_feed(b'<html>Blocked</html>','https://example.org')

    def test_failed_sources_not_empty_success(self):
        w=WatchedPage.objects.create(title='Fonte',url='https://example.org')
        j=CollectionJob.objects.create(source='paginas')
        with patch('core.collectors.fetch',side_effect=TimeoutError('Offline')):
            with self.assertRaises(ValueError):collect_sources(j)
        w.refresh_from_db();self.assertEqual(w.last_status,'error');self.assertIsNone(w.last_success_at)

    def test_schedule_save_pause_and_csrf(self):
        data={'name':'Todo dia 15','source':'pocos','enabled':'on','frequency':'monthly','interval_minutes':'60','at_time':'09:30','weekday':0,'monthday':15}
        self.assertEqual(self.client.post(f'/agenda/{self.s.pk}/',data).status_code,302)
        self.s.refresh_from_db();self.assertEqual(self.s.monthday,15);self.assertIsNotNone(self.s.next_run)
        self.client.post(f'/agenda/{self.s.pk}/acao/',{'action':'toggle'})
        self.s.refresh_from_db();self.assertFalse(self.s.enabled)
        c=Client(enforce_csrf_checks=True);c.force_login(self.user)
        self.assertEqual(c.post(f'/agenda/{self.s.pk}/acao/',{'action':'run'}).status_code,403)

    def test_scheduler_no_catchup_storm_and_serial(self):
        with tempfile.TemporaryDirectory() as tmp,self.settings(DATA_DIR=Path(tmp)):
            def start(source,parameters):return CollectionJob.objects.create(source=source,parameters=parameters)
            with patch('core.collectors.start_job',side_effect=start) as run:
                first=tick();self.assertIsNotNone(first)
                second=tick();self.assertIsNone(second)
                self.assertEqual(run.call_count,1)
            self.s.refresh_from_db();self.assertGreater(self.s.next_run,timezone.now())

    def test_resume_only_recent_partial(self):
        self.s.source='pncp_capacidades';self.s.last_job=CollectionJob.objects.create(source='pncp_capacidades',status='partial',parameters={'progress':{'PB':{'next_page':8}},'ufs':['PB']});self.s.save()
        self.assertEqual(schedule_parameters(self.s)['progress']['PB']['next_page'],8)
        self.s.last_job.status='ok';self.s.last_job.save()
        self.assertEqual(schedule_parameters(self.s)['progress'],{})

    def test_seed_preserves_existing_contact_and_schedule(self):
        from django.core.management import call_command
        self.c.do_not_contact=True;self.c.save()
        with tempfile.TemporaryDirectory() as tmp,self.settings(BASE_DIR=Path(tmp)):
            folder=Path(tmp)/'cartorios_cnj_20260918';folder.mkdir()
            record={'status':'Ativo','municipality':'João Pessoa','cns':'001234','name':'Nome antigo','source_url':'https://example.org','source_file':'cadastro','address':'Endereço antigo','attributes':'Outra atribuição','responsible':'Outro responsável','email':'old@example.org','phone':'0000'}
            (folder/'cadastros.json').write_text(json.dumps({'records':[record]}))
            call_command('configurar_central',verbosity=0)
            s=CollectionSchedule.objects.get(seed_key='pncp');s.enabled=False;s.interval_minutes=90;s.save()
            call_command('configurar_central',verbosity=0)
            self.org.refresh_from_db();self.c.refresh_from_db();s.refresh_from_db()
            self.assertEqual(self.org.address,'Rua A, 10');self.assertTrue(self.c.do_not_contact)
            self.assertEqual(self.org.contacts.count(),1);self.assertFalse(s.enabled);self.assertEqual(s.interval_minutes,90)

    def test_production_url_rejects_registered_environment_conflict(self):
        from .intelligence import collect_production_url
        j=CollectionJob.objects.create(source='producao_url',parameters={'url':'https://example.org/data.csv','environment':'Terra'})
        snap=Snapshot.objects.create(job=j,url='https://example.org',filename='test.csv',sha256='0'*64,size=1)
        Well.objects.create(source_id='test',registration='1',name='Teste',name_key='teste',uf='RN',environment='Mar',snapshot=snap)
        row={'uf':'RN','name_key':'teste','period':date(2026,1,1),'name':'Teste','environment':'Terra','petroleum':1,'gas':1,'raw':{}}
        with patch('core.collectors.validate_remote'),patch('core.collectors.fetch',return_value=(b'x',snap)),patch('core.wells.parse_production',return_value=([row],0)):
            with self.assertRaisesMessage(ValueError,'Ambiente diverge'):collect_production_url(j)
        self.assertFalse(WellProduction.objects.exists())

    def test_continuity_includes_schedule_and_source_health(self):
        from .monitoring import state_report,report_markdown
        WatchedPage.objects.create(title='Fonte indisponível',url='https://example.org',last_status='error',last_error='Timeout')
        report=state_report();text=report_markdown(report)
        self.assertIn('Poços semanal',text);self.assertIn('Timeout',text)
        self.assertIn('scheduler',report)
