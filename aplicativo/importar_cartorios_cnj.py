"""Importação local da consulta CNJ de 18/09/2026. Compatível com CartoGeo 0.1."""
import os,sys,re,json,unicodedata,hashlib,shutil
from pathlib import Path
from datetime import date
ROOT=Path(__file__).resolve().parent

def norm(value):
    return ' '.join(re.sub(r'[^a-z0-9 ]',' ',unicodedata.normalize('NFKD',str(value)).encode('ascii','ignore').decode().lower()).split())

def run():
    if not (ROOT/'manage.py').is_file() or not (ROOT/'cartogeo/settings.py').is_file():
        raise RuntimeError('Copie os arquivos deste pacote para a pasta aplicativo (a que contem manage.py).')
    os.chdir(ROOT);sys.path.insert(0,str(ROOT))
    from launch import local_lock
    app_lock=local_lock();collector_lock=local_lock('collection.lock')
    from django.conf import settings
    from django.db import transaction
    from django.utils import timezone
    from django.core.validators import validate_email
    from core.models import Organization,Contact,Municipality,CollectionJob,Snapshot
    from core.backup import create_backup
    folder=ROOT/'cartorios_cnj_20260918';raw=(folder/'cadastros.json').read_bytes()
    data=json.loads(raw);all_rows=data['records'];rows=[r for r in all_rows if r['status']=='Ativo']
    if len(all_rows)!=81 or len(rows)!=78 or len({r['cns'] for r in all_rows})!=81:
        raise RuntimeError('O pacote de dados nao corresponde a consulta validada. Nada foi importado.')
    municipalities={norm(m.name):m for m in Municipality.objects.filter(uf='PB')}
    if not municipalities:raise RuntimeError('Execute primeiro a coleta IBGE no aplicativo.')
    existing=list(Organization.objects.filter(kind='cartorio'));plan=[];skipped=[];warnings=[]
    for r in rows:
        if not re.fullmatch(r'\d{6}',r['cns']):raise ValueError('CNS invalido')
        validate_email(r['email'])
        mun=municipalities.get(norm(r['municipality']))
        same_id=[o for o in existing if re.sub(r'\D','',o.cnpj)==r['cns']]
        same_name=[o for o in existing if norm(o.name)==norm(r['name']) and (not mun or o.municipality_id==mun.pk)]
        if same_id or same_name:
            skipped.append(r['cns']+' — '+r['municipality']+': cadastro existente preservado; conferir eventuais diferencas.')
            continue
        if mun is None:warnings.append(r['cns']+' — municipio nao conciliado: '+r['municipality']+'; nome preservado em Observacoes.')
        name=(r['name'][:209]+' — CNS '+r['cns'])
        notes=(f"Consulta CNJ: 18/09/2026. CNS: {r['cns']}.\nSituacao na fonte: {r['status']}. Delegacao: {r['delegation']}.\n"
               f"Denominacao integral: {r['name']}\nMunicipio informado pelo CNJ: {r['municipality']}/PB\n"
               f"Endereco publicado: {r['address']}\nAtribuicoes: {r['attributes']}\nResponsavel publicado: {r['responsible']}\n"
               f"Site informado na fonte: {r['website']}\nDocumento: {r['source_file']}\n"
               "Contato extraido de cadastro publico; atendimento ainda nao confirmado. Coordenadas nao importadas.\n")
        if r['cns']=='071837':notes+='Conceicao confirmado no cadastro CNJ; desconsiderar associacao e coordenadas anteriores de Taperoa.\n'
        site=r['website'] if r['website'].startswith(('https://','http://')) and r['website'] not in ('http://','https://') else ''
        org=Organization(name=name,kind='cartorio',role='institucional',municipality=mun,cnpj=r['cns'],website=site,source_url=r['source_url'],verified_on=date(2026,9,18),notes=notes)
        org.full_clean();plan.append((r,org))
    for file in folder.glob('*.pdf'):
        if not file.is_file():raise RuntimeError('Falta documento de origem.')
    print(f'Consulta: 81 cadastros; 78 ativos; 3 inativos mantidos somente nos arquivos de referencia.')
    print(f'A cadastrar: {len(plan)}. Ja existentes/preservados: {len(skipped)}. Municipios a conferir: {len(warnings)}.')
    if not plan:
        print('Nenhum novo cadastro. Importacao ja aplicada ou registros existentes.');return
    backup=create_backup();print('Backup anterior criado:',backup)
    job=None;dest=None
    try:
        with transaction.atomic():
            job=CollectionJob.objects.create(source='cartorios_cnj',status='running',parameters={'consulta':'2026-09-18','tipo':'importacao_local'})
            dest=settings.DATA_DIR/'fontes'/str(job.pk);dest.mkdir(parents=True,exist_ok=True)
            for file in [folder/'cadastros.json',*sorted(folder.glob('*.pdf'))]:
                payload=file.read_bytes();shutil.copy2(file,dest/file.name)
                Snapshot.objects.create(job=job,url=rows[0]['source_url'],filename=file.name,sha256=hashlib.sha256(payload).hexdigest(),size=len(payload))
            for r,org in plan:
                org.save()
                contact=Contact(organization=org,name=r['responsible'],position='Responsavel informado pelo CNJ',email=r['email'],phone=r['phone'],source_url=r['source_url'],verified_on=date(2026,9,18),notes='Dados publicados na consulta de 18/09/2026. Telefone/e-mail ainda nao confirmados por atendimento.')
                contact.full_clean();contact.save()
            job.status='partial' if warnings or skipped else 'ok'
            job.summary=f'{len(plan)} organizacoes e {len(plan)} contatos cadastrados. {len(skipped)} cadastros existentes preservados. 3 inativos mantidos apenas nos arquivos de origem.\n'+'\n'.join(warnings+skipped)
            job.finished_at=timezone.now();job.save()
    except Exception:
        if dest and dest.is_dir():shutil.rmtree(dest)
        raise
    print('\nIMPORTACAO CONCLUIDA. Abra 02_ABRIR.bat e consulte Organizacoes e Contatos.')
    print('Em Fontes e coletas, abra CARTORIOS_CNJ para consultar o resumo e os documentos.')
    for warning in warnings+skipped:print(warning)

if __name__=='__main__':
    try:run()
    except (Exception,SystemExit) as exc:
        print('\nNao foi possivel concluir:',exc)
        print('Se o aplicativo estiver aberto, encerre-o com Ctrl+C na janela do programa e tente novamente.')
        sys.exit(1)
