import io
import json
import zipfile
from django.test import TestCase, Client
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from .models import Municipality, Signal, InternalPlan, InternalPlanLog, Opportunity

class TerritoryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user=get_user_model().objects.create_user('territory-test',password='only-for-test-123')
        call_command('configurar_territorio',stdout=io.StringIO())
    def setUp(self):self.client.force_login(self.user)

    def test_catalog_and_preserve_decisions(self):
        self.assertEqual(Municipality.objects.count(),751)
        self.assertEqual(InternalPlan.objects.count(),3)
        self.assertEqual(Opportunity.objects.count(),0)
        s=Signal.objects.first();s.status='descartado';s.review_note='Manter minha decisão';s.save()
        p=InternalPlan.objects.first();p.notes='Minha anotação';p.status='escopo';p.save()
        m=Municipality.objects.get(pk='2503209');m.source_url='https://example.org/fonte-validada';m.save()
        call_command('configurar_territorio',stdout=io.StringIO())
        s.refresh_from_db();p.refresh_from_db();m.refresh_from_db()
        self.assertEqual(s.status,'descartado');self.assertEqual(s.review_note,'Manter minha decisão')
        self.assertEqual(p.notes,'Minha anotação');self.assertEqual(p.status,'escopo')
        self.assertEqual(m.source_url,'https://example.org/fonte-validada')
        self.assertEqual(InternalPlanLog.objects.count(),3)

    def test_authenticated_pages_and_references(self):
        paths=['/planejamento/','/planejamento/novo/','/planejamento/continuidade.md','/municipios/?uf=PB',
               '/pocos/mapa/?uf=PB&municipio=2503209','/referencia-interna/casa_legal_capa.jpeg/']
        for p in paths:
            r=self.client.get(p);self.assertEqual(r.status_code,200,p);r.close()
        self.client.logout()
        for p in paths:self.assertEqual(self.client.get(p).status_code,302,p)

    def test_plan_edit_log_and_csrf(self):
        p=InternalPlan.objects.first()
        data=dict(title=p.title,municipality=p.municipality_id,category=p.category,status='diagnostico',
                  owner='Uendry',next_action='Conferir ato oficial',due_date='',blockers='Ato pendente',notes='Revisado')
        secure=Client(enforce_csrf_checks=True);secure.force_login(self.user)
        self.assertEqual(secure.post(f'/planejamento/{p.pk}/',data).status_code,403)
        self.assertEqual(self.client.post(f'/planejamento/{p.pk}/',data).status_code,302)
        p.refresh_from_db();self.assertEqual(p.notes,'Revisado')
        self.assertEqual(p.history.first().changes['status'],'diagnostico')

    def test_layers_integrity_and_offline_package(self):
        response=self.client.get('/pocos/cartografia.zip?uf=PB')
        self.assertEqual(response.status_code,200)
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            self.assertIsNone(z.testzip());page=z.read('mapa.html').decode()
            for marker in ['__WELLS_DATA__','__MUNICIPALITIES_DATA__','__LINES_DATA__']:self.assertNotIn(marker,page)
            self.assertIn('territorio_map.js',z.namelist())
            m=json.loads(z.read('municipios_ibge.geojson'));l=json.loads(z.read('linhas_lbr.geojson'))
            self.assertEqual(len(m['features']),751);self.assertEqual(len(l['features']),279)
            self.assertEqual(len({f['properties']['codigo_ibge'] for f in m['features']}),751)
            self.assertTrue(all(f['geometry']['type']=='LineString' for f in l['features']))
            self.assertTrue(all(f['properties']['src_original']=='EPSG:4674 / SIRGAS 2000' for f in l['features']))

    def test_factual_dates_and_no_unverified_cadastral_title(self):
        cadastral=Signal.objects.get(kind='cadastral')
        self.assertIsNone(cadastral.payload['date']);self.assertIsNone(cadastral.payload['quantity'])
        historic=Signal.objects.get(external_key='cabedelo:habita:jacare:2022-08-11')
        self.assertEqual(historic.payload['quantity'],84)
        self.assertIsNone(historic.deadline)
        self.assertContains(self.client.get(f'/sinais/{historic.pk}/'),'value="urbano" selected')
        self.assertEqual(self.client.get('/referencia-interna/secret.key/').status_code,404)
