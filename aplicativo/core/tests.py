import io
import tempfile
import zipfile
from datetime import date
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch
from django.test import TestCase,Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from .models import *
from .collectors import pncp_signal,parse_anp_xlsx,money,normalize

class WorkflowTests(TestCase):
    def setUp(self):
        self.user=get_user_model().objects.create_user('tester',password='test-only-password')
        self.client.force_login(self.user)
        self.m=Municipality.objects.create(code='2507507',name='João Pessoa',uf='PB',source_url='https://example.org')
        self.org=Organization.objects.create(name='Organização de teste',kind='empresa',municipality=self.m)
        self.o=Opportunity.objects.create(title='Oportunidade de teste',organization=self.org,front='apoio',next_action='Conferir escopo')
        self.s=Signal.objects.create(title='Sinal de teste',kind='edital',external_key='test',source_url='https://example.org',reason='Conferir edital')
        self.j=CollectionJob.objects.create(source='pncp',status='ok')

    def test_pages_and_authentication(self):
        paths=['/','/sinais/','/sinais/novo/',f'/sinais/{self.s.pk}/','/royalties/',f'/municipios/{self.m.pk}/',f'/oportunidade/{self.o.pk}/',f'/oportunidade/{self.o.pk}/briefing/','/fontes/',f'/coletas/{self.j.pk}/','/backup/','/ajuda/','/exportar/oportunidades/']
        for entity in ['organizacoes','contatos','oportunidades','planos','financeiro','paginas']:
            paths += [f'/{entity}/',f'/{entity}/novo/']
        for path in paths:
            with self.subTest(path=path):self.assertEqual(self.client.get(path).status_code,200)
        self.client.logout()
        for path in paths:self.assertEqual(self.client.get(path).status_code,302)
        self.assertEqual(self.client.get('/entrar/').status_code,200)

    def test_commercial_flow(self):
        r=self.client.post('/oportunidades/novo/',dict(title='Levantamento',organization=self.org.pk,front='apoio',stage='qualificada',route='direta',priority=1,owner='Uendry',next_action='Agendar diagnóstico'))
        self.assertEqual(r.status_code,302)
        o=Opportunity.objects.get(title='Levantamento')
        self.assertEqual(o.activities.count(),1)
        self.client.post(f'/oportunidade/{o.pk}/historico/',{'kind':'contato','text':'Necessidade confirmada em reunião'})
        self.assertEqual(o.activities.exclude(kind='sistema').count(),1)
        self.assertEqual(o.activities.filter(kind='sistema',text__startswith='Cadência').count(),1)
        with tempfile.TemporaryDirectory() as tmp,self.settings(MEDIA_ROOT=tmp):
            r=self.client.post(f'/oportunidade/{o.pk}/documento/',{'title':'Escopo v1','file':SimpleUploadedFile('escopo.txt',b'conteudo')})
            self.assertEqual(r.status_code,302)
            a=o.attachments.get()
            response=self.client.get(f'/documento/{a.pk}/')
            self.assertEqual(b''.join(response.streaming_content),b'conteudo')
        self.client.post('/financeiro/novo/',dict(opportunity=o.pk,description='Parcela 1',kind='honorarios',amount='100',status='realizada',due_date=date.today(),received_date=date.today(),evidence='Comprovante'))
        self.assertEqual(o.cash_entries.count(),1)

    def test_recollection_preserves_review(self):
        item={'objetoCompra':'Serviços de georreferenciamento','numeroControlePNCP':'123','orgaoEntidade':{'cnpj':'12345678000199'},'anoCompra':2026,'sequencialCompra':1}
        pncp_signal(item,self.j,'georreferenciamento')
        s=Signal.objects.get(external_key='pncp:123');s.status='descartado';s.review_note='Fora do escopo';s.save()
        pncp_signal(item,self.j,'georreferenciamento')
        s.refresh_from_db();self.assertEqual(s.status,'descartado');self.assertEqual(s.review_note,'Fora do escopo')
        self.assertEqual(Signal.objects.filter(external_key='pncp:123').count(),1)

    def test_financial_validation_and_csrf(self):
        with self.assertRaises(ValidationError):CashEntry(opportunity=self.o,description='Falso recebimento',kind='exito',amount=100,status='realizada',due_date=date.today()).full_clean()
        secure=Client(enforce_csrf_checks=True);secure.force_login(self.user)
        self.assertEqual(secure.post(f'/municipios/{self.m.pk}/sinal/').status_code,403)
        self.assertEqual(self.client.get('/backup/baixar/').status_code,405)
        self.assertEqual(money('1.234,56'),Decimal('1234.56'))
        with self.assertRaises(ValueError):money(None)

    def test_signal_conversion_idempotent(self):
        payload=dict(title='Demanda revisada',organization=self.org.pk,front='apoio',stage='identificada',route='direta',priority=2,owner='Uendry',next_action='Conferir escopo',action='convert')
        for _ in range(2):self.assertEqual(self.client.post(f'/sinais/{self.s.pk}/',payload).status_code,302)
        self.assertEqual(Opportunity.objects.filter(signal=self.s).count(),1)

    def test_anp_unpublished_months(self):
        from openpyxl import Workbook
        book=Workbook();sheet=book.active;sheet.title='TOTAL'
        sheet.append(['ROYALTIES 2026']);sheet.append(['UF','Beneficiário']+['Royalties até 5%','Royalties excedentes','Total']*12)
        sheet.append([None,'MUNICIPIOS',100,50,150]+[None]*33)
        sheet.append(['PB','João Pessoa-PB',100,50,150]+[None]*33)
        buffer=io.BytesIO();book.save(buffer)
        records,months,missing=parse_anp_xlsx(buffer.getvalue(),2026,{('PB',normalize('João Pessoa')):self.m.pk})
        self.assertEqual(months,[1]);self.assertEqual(len(records),1);self.assertEqual(records[0]['total'],Decimal('150'))
        sheet.cell(4,5,160);buffer=io.BytesIO();book.save(buffer)
        with self.assertRaises(ValueError):parse_anp_xlsx(buffer.getvalue(),2026,{('PB',normalize('João Pessoa')):self.m.pk})
