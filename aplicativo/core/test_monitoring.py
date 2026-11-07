import json,tempfile,zipfile,hashlib,importlib.util
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
from django.test import TestCase,Client
from django.contrib.auth import get_user_model
from django.conf import settings
from .models import CollectionJob,Signal,Snapshot,InternalPlan
from .bid_scans import default_parameters,collect_capabilities
from .monitoring import build_bundle,state_report

class MonitoringTests(TestCase):
    def setUp(self):
        self.user=get_user_model().objects.create_user('monitor',password='testonly-123456')
        self.client.force_login(self.user)
    def test_failure_continues_and_resume_preserves_review(self):
        j=CollectionJob.objects.create(source='pncp_capacidades',parameters=default_parameters(['geodados'],['PB','RN'],1))
        item={'objetoCompra':'Serviços de geoprocessamento','numeroControlePNCP':'123','orgaoEntidade':{'cnpj':'12345678000199'},'anoCompra':2026,'sequencialCompra':1}
        def fake(url,*a,**kw):
            if 'uf=PB' in url:raise TimeoutError('teste')
            return json.dumps({'data':[item],'totalPaginas':1}).encode(),SimpleNamespace(pk=99,sha256='a'*64)
        with patch('core.collectors.fetch',side_effect=fake):summary,partial=collect_capabilities(j)
        self.assertTrue(partial);self.assertFalse(j.parameters['progress']['PB']['done']);self.assertTrue(j.parameters['progress']['RN']['done'])
        signal=Signal.objects.get();signal.status='descartado';signal.review_note='Decisão preservada';signal.save()
        j2=CollectionJob.objects.create(source='pncp_capacidades',parameters=j.parameters)
        with patch('core.collectors.fetch',return_value=(b'{"data":[],"empty":true}',SimpleNamespace(pk=100,sha256='b'*64))) as f:
            _,partial=collect_capabilities(j2);self.assertEqual(f.call_count,1)
        self.assertFalse(partial);self.assertEqual(Signal.objects.count(),1)
        signal.refresh_from_db();self.assertEqual(signal.review_note,'Decisão preservada')
    def test_http_body_and_provenance(self):
        from .collectors import fetch
        import gzip
        body=gzip.compress(b'{"data":[]}')
        class Response:
            status=200;headers={'Content-Type':'application/json','Content-Encoding':'gzip'}
            def geturl(self):return 'https://pncp.gov.br/example'
            def read(self,n):return body
            def __enter__(self):return self
            def __exit__(self,*args):pass
        j=CollectionJob.objects.create(source='test')
        with tempfile.TemporaryDirectory() as tmp,self.settings(DATA_DIR=Path(tmp)),patch('core.collectors.validate_remote'),patch('core.collectors.urllib.request.build_opener') as mock:
            mock.return_value.open.return_value=Response();raw,s=fetch('https://pncp.gov.br/example',j,'json',attempts=1)
            self.assertEqual(raw,b'{"data":[]}');self.assertEqual(s.provenance['status'],200)
            file=Path(tmp)/'fontes'/str(j.pk)/s.provenance['received_body_file'];self.assertEqual(file.read_bytes(),body)
            self.assertEqual(s.provenance['received_body_sha256'],hashlib.sha256(body).hexdigest())
    def test_bundle_integrity_tampering_and_missing_source(self):
        spec=importlib.util.spec_from_file_location('verify_bundle',settings.BASE_DIR/'scripts/verificar_pacote.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
        with tempfile.TemporaryDirectory() as tmp,self.settings(DATA_DIR=Path(tmp)):
            path=build_bundle();self.assertGreater(mod.verify(path),0)
            corrupt=Path(tmp)/'corrupt.zip'
            with zipfile.ZipFile(path) as src,zipfile.ZipFile(corrupt,'w') as dest:
                for name in src.namelist():dest.writestr(name,b'ALTERADO' if name=='ESTADO.json' else src.read(name))
            with self.assertRaises(ValueError):mod.verify(corrupt)
            j=CollectionJob.objects.create(source='test',status='ok')
            Snapshot.objects.create(job=j,url='https://example.org',filename='missing.json',sha256='a'*64,size=3)
            with self.assertRaises(ValueError):build_bundle(evidence=True)
    def test_monitor_auth_csrf_and_active_collection(self):
        self.assertEqual(self.client.get('/acompanhamento/').status_code,200)
        secure=Client(enforce_csrf_checks=True);secure.force_login(self.user)
        self.assertEqual(secure.post('/acompanhamento/exportar/acompanhamento/').status_code,403)
        self.assertEqual(self.client.get('/acompanhamento/exportar/dossie/').status_code,405)
        with tempfile.TemporaryDirectory() as tmp,self.settings(DATA_DIR=Path(tmp)):
            CollectionJob.objects.create(source='pncp_capacidades',status='running')
            self.assertEqual(self.client.post('/acompanhamento/exportar/dossie/').status_code,302)
        self.client.logout();self.assertEqual(self.client.get('/acompanhamento/').status_code,302)
    def test_overdue_task_and_report_includes_blockers(self):
        from datetime import timedelta
        from django.utils import timezone
        InternalPlan.objects.create(title='Pendência',category='operacao',next_action='Revisar',blockers='Documento faltante',due_date=timezone.localdate()-timedelta(days=1))
        report=state_report();self.assertTrue(report['plans'][0]['overdue']);self.assertEqual(report['plans'][0]['blockers'],'Documento faltante')
