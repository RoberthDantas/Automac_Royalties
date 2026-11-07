import json
import re
from datetime import date, time, timedelta
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from core.models import Organization, Contact, Municipality, WatchedPage, CollectionSchedule
from core.collectors import normalize
from core.intelligence import ALL_TERMS
from core.scheduling import next_occurrence

class Command(BaseCommand):
    help='Prepara contatos, agenda e fontes; preserva alterações existentes.'

    @transaction.atomic
    def handle(self,*args,**options):
        path=settings.BASE_DIR/'cartorios_cnj_20260918/cadastros.json'
        count=0
        if path.exists():
            rows=json.loads(path.read_text(encoding='utf-8'))['records']
            municipalities={normalize(m.name):m for m in Municipality.objects.filter(uf='PB')}
            for r in rows:
                if r['status']!='Ativo':continue
                mun=municipalities.get(normalize(r['municipality']))
                if not mun:continue
                org=next((o for o in Organization.objects.filter(kind='cartorio') if re.sub(r'\D','',o.cnpj)==r['cns']),None)
                created=False
                if org is None:
                    org,created=Organization.objects.get_or_create(name=r['name'][:209]+' — CNS '+r['cns'],kind='cartorio',defaults={
                        'role':'institucional','cnpj':r['cns'],'municipality':mun,'source_url':r['source_url'],
                        'verified_on':date(2026,9,18),'notes':'Consulta CNJ em 18/09/2026. Atendimento não confirmado. Fonte: '+r['source_file']})
                fields=[]
                if not org.address:org.address=r['address'];fields.append('address')
                if not org.attributes:org.attributes=r['attributes'];fields.append('attributes')
                if fields:org.save(update_fields=fields)
                if created or not org.contacts.exists():
                    Contact.objects.get_or_create(organization=org,name=r['responsible'],email=r['email'],phone=r['phone'],defaults={
                        'position':'Responsável publicado pelo CNJ','source_url':r['source_url'],'verified_on':date(2026,9,18),
                        'notes':'Cadastro público histórico; conferir atendimento antes de usar.'})
                count+=created
        # Original addresses are landing pages, not guessed feed endpoints.
        for title,url,code in [
            ('Prefeitura de João Pessoa — publicações','https://www.joaopessoa.pb.gov.br/','2507507'),
            ('Prefeitura de Cabedelo — publicações','https://cabedelo.pb.gov.br/','2503209'),
            ('Ministério das Cidades — notícias','https://www.gov.br/cidades/pt-br/assuntos/noticias',None),
            ('INCRA — notícias','https://www.gov.br/incra/pt-br/assuntos/noticias',None)]:
            WatchedPage.objects.get_or_create(url=url,defaults={'title':title,'kind':'fundiaria','keywords':'reurb, regularização fundiária, plano diretor, georreferenciamento, cadastro territorial, topografia, cartografia, licenciamento ambiental, loteamento, empreendimento habitacional, royalties',
                'municipality':Municipality.objects.filter(pk=code).first() if code else None})
        defaults=[
            ('pncp','PNCP · radar a cada 12 horas','pncp_capacidades','interval',720,0,20),
            ('diarios','Diários · checagem diária','diarios','interval',1440,0,20),
            ('paginas','Fontes públicas e privadas · a cada 2 horas','paginas','interval',120,0,20),
            ('pocos','Cadastro de poços · segunda às 08h','pocos','weekly',60,0,20),
            ('royalties','Royalties · dia 20 às 09h','anp','monthly',60,0,20)]
        for i,(key,name,source,freq,interval,weekday,monthday) in enumerate(defaults):
            s,created=CollectionSchedule.objects.get_or_create(seed_key=key,defaults={'name':name,'source':source,'frequency':freq,
                'interval_minutes':interval,'weekday':weekday,'monthday':monthday,'at_time':time(9 if source=='anp' else 8),
                'parameters':{'ufs':['PB','RN','CE','SE','AL']} if source in ('diarios','pncp_capacidades') else {}})
            # 0.4.2: rotinas ainda com a frequência original da 0.4.1 passam ao novo padrão; ajustes seus são preservados.
            if not created and (key,s.interval_minutes) in (('pncp',30),('diarios',360)) and s.frequency=='interval':
                s.interval_minutes=interval;s.name=name
                s.next_run=next_occurrence(s)
                s.save(update_fields=['interval_minutes','name','next_run'])
            if created:
                s.next_run=timezone.now()+timedelta(minutes=i) if freq=='interval' else next_occurrence(s)
                s.save(update_fields=['next_run'])
        self.stdout.write(f'Central preparada: {count} cartórios novos; endereços complementados sem alterar contatos existentes.')
