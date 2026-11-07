"""Correções da 0.5.3: contagem do painel, pausa do PNCP (HTTP 429), retorno seguro após conferir contato, rótulo do acumulado."""
import json,urllib.error
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from .models import CollectionJob,Organization,Contact,Opportunity,Municipality,Royalty,Snapshot
from .bid_scans import default_parameters,collect_capabilities
from .collectors import FetchUnavailable


class Release053Tests(TestCase):
    def setUp(self):
        self.user=get_user_model().objects.create_user('t053',password='testonly-123456',first_name='Teste')
        self.client.force_login(self.user)
        self.org=Organization.objects.create(name='Prefeitura X',kind='prefeitura')

    def test_dashboard_counts_all_overdue_actions(self):
        past=timezone.localdate()-timedelta(days=3)
        for i in range(20):
            Opportunity.objects.create(title=f'Op {i}',organization=self.org,front='royalties',next_action='Ligar',next_date=past)
        r=self.client.get('/')
        self.assertEqual(r.context['tasks_total'],20)
        self.assertEqual(len(r.context['tasks']),12)
        self.assertContains(r,'<b>20</b><small>Ações vencendo hoje ou atrasadas</small>',html=False)

    def test_pncp_429_stops_round_and_resumes(self):
        j=CollectionJob.objects.create(source='pncp_capacidades',parameters=default_parameters(['geodados'],['PB','RN','CE'],5))
        calls=[]
        def fake(url,*a,**kw):
            calls.append(url)
            self.assertEqual(kw.get('attempts'),3)
            if 'uf=RN' in url:
                err=urllib.error.HTTPError(url,429,'Too Many Requests',{},None)
                raise FetchUnavailable('Sem resposta completa após 3 tentativas (HTTP 429).') from err
            return json.dumps({'data':[],'totalPaginas':1}).encode(),SimpleNamespace(pk=1,sha256='a'*64)
        with patch('core.collectors.fetch',side_effect=fake),patch('core.bid_scans.time.sleep') as sleep:
            summary,partial=collect_capabilities(j)
        self.assertTrue(partial)
        self.assertTrue(j.parameters['progress']['PB']['done'])
        self.assertIn('429',j.parameters['progress']['RN']['error'])
        self.assertNotIn('CE',j.parameters['progress'])          # não insistiu na UF seguinte
        self.assertFalse(any('uf=CE' in u for u in calls))
        self.assertEqual(sleep.call_count,1)                     # pausa entre a 1ª e a 2ª página
        self.assertIn('pediu pausa',summary)
        j2=CollectionJob.objects.create(source='pncp_capacidades',parameters=j.parameters)
        with patch('core.collectors.fetch',return_value=(b'{"data":[],"empty":true}',SimpleNamespace(pk=2,sha256='b'*64))),patch('core.bid_scans.time.sleep'):
            _,partial=collect_capabilities(j2)
        self.assertFalse(partial)
        self.assertTrue(all(j2.parameters['progress'][uf]['done'] for uf in ('PB','RN','CE')))

    def test_verify_contact_does_not_redirect_outside(self):
        c=Contact.objects.create(organization=self.org,name='Procuradoria')
        r=self.client.post(f'/contatos/{c.pk}/conferir/',{'next':'https://exemplo.com/'})
        self.assertEqual(r['Location'],'/contatos/')
        r=self.client.post(f'/contatos/{c.pk}/conferir/',{'next':'/oportunidade/1/'})
        self.assertEqual(r['Location'],'/oportunidade/1/')

    def test_ytd_label_uses_month_names(self):
        from .importer import royalty_ytd
        m=Municipality.objects.create(code='2400000',name='Teste',uf='RN',source_url='https://ibge.gov.br')
        job=CollectionJob.objects.create(source='anp')
        snap=Snapshot.objects.create(job=job,url='https://anp.gov.br',filename='x',sha256='c'*64,size=1)
        for year in (2025,2026):
            for month in (3,4):
                Royalty.objects.create(municipality=m,year=year,month=month,minimum=1,excess=1,total=2,source_url='https://anp.gov.br',snapshot=snap)
        label,_=royalty_ytd([m.code])
        self.assertEqual(label,'2026 (mar–abr) vs 2025')
