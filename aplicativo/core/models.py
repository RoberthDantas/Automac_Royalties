from datetime import date
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, URLValidator
from django.core.exceptions import ValidationError
from django.utils import timezone

FRONTS = [('royalties','Royalties e águas territoriais'), ('risco','Inteligência territorial e risco'),
          ('rural','Georreferenciamento rural e SIGEF'), ('urbano','REURB e cadastro urbano'),
          ('cursos','Capacitação'), ('marinha','Terrenos de marinha'), ('apoio','Apoio técnico a empresas e escritórios')]
STAGES = [('identificada','Identificada'),('qualificada','Qualificada'),('contato','Contato realizado'),
          ('diagnostico','Diagnóstico'),('proposta','Proposta enviada'),('negociacao','Negociação'),
          ('contratada','Contratada'),('execucao','Em execução'),('concluida','Concluída'),
          ('suspensa','Suspensa'),('perdida','Perdida')]
SIGNAL_KINDS = [('edital','Edital'),('royalties','Royalties'),('plano','Plano diretor'),('contato','Contato institucional'),('fundiaria','Ação de regularização fundiária'),('cadastral','Atualização cadastral municipal'),('outro','Outro gatilho')]
HTTP_VALIDATOR = URLValidator(schemes=['https','http'])

class InternalPlan(models.Model):
    title = models.CharField('Ação interna', max_length=240)
    seed_key = models.CharField(max_length=250, unique=True, null=True, blank=True, editable=False)
    signal = models.ForeignKey('Signal', on_delete=models.PROTECT, null=True, blank=True, verbose_name='Evidência no radar')
    municipality = models.ForeignKey('Municipality', on_delete=models.PROTECT, null=True, blank=True, verbose_name='Município')
    category = models.CharField('Frente de trabalho', max_length=20, choices=[('fundiaria','Regularização fundiária'),('cadastral','Cadastro territorial'),('cartografia','Cartografia'),('operacao','Operação interna')])
    status = models.CharField('Etapa interna', max_length=20, default='verificar', choices=[('verificar','Verificar evidência'),('diagnostico','Diagnóstico interno'),('escopo','Preparar escopo'),('decisao','Aguardar decisão da direção'),('concluido','Concluído'),('suspenso','Suspenso')])
    owner = models.CharField('Responsável', max_length=100, default='A definir')
    next_action = models.CharField('Próxima ação', max_length=500)
    due_date = models.DateField('Prazo definido por você', null=True, blank=True)
    blockers = models.TextField('Pendências e condições', blank=True)
    notes = models.TextField('Notas e resultado', blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['status','due_date','title']

class InternalPlanLog(models.Model):
    plan = models.ForeignKey(InternalPlan, on_delete=models.CASCADE, related_name='history')
    author = models.CharField(max_length=150)
    changes = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at']

class Municipality(models.Model):
    code = models.CharField('Código IBGE', max_length=7, primary_key=True)
    name = models.CharField('Município', max_length=160)
    uf = models.CharField('UF', max_length=2)
    source_url = models.URLField('Fonte', max_length=1000)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['uf','name']
    def __str__(self): return f'{self.name} / {self.uf}'

class Organization(models.Model):
    address = models.TextField('Endereço publicado', blank=True)
    attributes = models.TextField('Atribuições da serventia', blank=True)
    name = models.CharField('Nome da organização', max_length=240)
    kind = models.CharField('Tipo',max_length=30,choices=[('prefeitura','Prefeitura'),('cartorio','Cartório'),('escritorio','Escritório de advocacia'),('empresa','Empresa'),('orgao','Órgão público'),('parceiro','Parceiro'),('outro','Outro')])
    role = models.CharField('Papel no relacionamento',max_length=20,choices=[('avaliar','A identificar'),('comprador','Possível comprador'),('institucional','Interlocutor institucional'),('parceiro','Possível parceiro')],default='avaliar')
    municipality = models.ForeignKey(Municipality, verbose_name='Município',on_delete=models.PROTECT,null=True,blank=True)
    cnpj = models.CharField('CNPJ ou CNS',max_length=30,blank=True)
    website = models.URLField('Site oficial',max_length=1000,blank=True,validators=[HTTP_VALIDATOR])
    source_url = models.URLField('Fonte do cadastro',max_length=1000,blank=True,validators=[HTTP_VALIDATOR])
    verified_on = models.DateField('Data de conferência',null=True,blank=True)
    notes = models.TextField('Observações',blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['name']
        constraints=[models.UniqueConstraint(fields=['name','kind'],name='organization_name_kind')]
    def __str__(self): return self.name

class Contact(models.Model):
    organization = models.ForeignKey(Organization,verbose_name='Organização',on_delete=models.CASCADE,related_name='contacts')
    name = models.CharField('Nome ou setor',max_length=180)
    position = models.CharField('Cargo ou função',max_length=180,blank=True)
    email = models.EmailField('E-mail institucional',blank=True)
    phone = models.CharField('Telefone',max_length=80,blank=True)
    source_url = models.URLField('Fonte',max_length=1000,blank=True,validators=[HTTP_VALIDATOR])
    verified_on = models.DateField('Conferido em',null=True,blank=True)
    do_not_contact = models.BooleanField('Não contatar',default=False)
    notes = models.TextField('Observações',blank=True)
    class Meta:
        ordering=['organization__name','name']
        constraints=[models.UniqueConstraint(fields=['organization','name','email','phone'],name='contact_identity')]
    def __str__(self):return f'{self.name} — {self.organization}'

class CollectionJob(models.Model):
    source = models.CharField(max_length=40)
    status = models.CharField(max_length=16,default='queued',choices=[('queued','Na fila'),('running','Coletando'),('ok','Concluída'),('partial','Parcial'),('error','Falhou')])
    parameters = models.JSONField(default=dict)
    summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True,blank=True)
    class Meta: ordering=['-created_at']

class Snapshot(models.Model):
    job = models.ForeignKey(CollectionJob,on_delete=models.CASCADE,related_name='snapshots')
    url = models.URLField(max_length=2000)
    filename = models.CharField(max_length=200)
    sha256 = models.CharField(max_length=64)
    size = models.PositiveIntegerField()
    provenance = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Signal(models.Model):
    source_type = models.CharField(max_length=20, default='manual', db_index=True)
    publication_date = models.DateField(null=True, blank=True, db_index=True)
    last_seen_at = models.DateTimeField(null=True, blank=True)
    relevance = models.PositiveSmallIntegerField(default=0, db_index=True)
    title = models.CharField('Título',max_length=500)
    kind = models.CharField('Tipo',max_length=20,choices=SIGNAL_KINDS)
    municipality = models.ForeignKey(Municipality,on_delete=models.SET_NULL,null=True,blank=True)
    external_key = models.CharField(max_length=250,unique=True)
    source_url = models.URLField('Fonte',max_length=2000)
    reason = models.TextField('Motivo da seleção')
    payload = models.JSONField(default=dict)
    deadline = models.DateTimeField('Prazo na fonte',null=True,blank=True)
    status = models.CharField(max_length=20,default='novo',choices=[('novo','A revisar'),('descartado','Descartado'),('convertido','Em acompanhamento')])
    review_note = models.TextField(blank=True)
    job = models.ForeignKey(CollectionJob,on_delete=models.SET_NULL,null=True,blank=True)
    collected_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: ordering=['-updated_at']
    @property
    def is_closed(self):return bool(self.deadline and self.deadline < timezone.now())

class Royalty(models.Model):
    municipality = models.ForeignKey(Municipality,on_delete=models.PROTECT)
    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField(validators=[MinValueValidator(1),MaxValueValidator(12)])
    minimum = models.DecimalField(max_digits=20,decimal_places=2)
    excess = models.DecimalField(max_digits=20,decimal_places=2)
    total = models.DecimalField(max_digits=20,decimal_places=2)
    source_url = models.URLField(max_length=2000)
    snapshot = models.ForeignKey(Snapshot,on_delete=models.PROTECT)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering=['-year','-month','municipality__name']
        constraints=[models.UniqueConstraint(fields=['municipality','year','month'],name='royalty_municipal_period')]

class Well(models.Model):
    source_id = models.CharField(max_length=64,primary_key=True)
    registration = models.CharField('Cadastro ANP',max_length=40,db_index=True)
    name = models.CharField('Poço ANP',max_length=120,db_index=True)
    name_key = models.CharField(max_length=120,db_index=True)
    uf = models.CharField(max_length=2,db_index=True)
    operator = models.CharField(max_length=200,blank=True)
    basin = models.CharField(max_length=150,blank=True)
    field = models.CharField(max_length=150,blank=True)
    environment = models.CharField(max_length=20,blank=True)
    situation = models.CharField(max_length=200,blank=True)
    longitude = models.FloatField(null=True)
    latitude = models.FloatField(null=True)
    original_datum = models.CharField(max_length=100,blank=True)
    properties = models.JSONField(default=dict)
    snapshot = models.ForeignKey(Snapshot,on_delete=models.PROTECT)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: ordering=['uf','name']

class WellProduction(models.Model):
    name_key = models.CharField(max_length=120)
    name = models.CharField(max_length=120)
    uf = models.CharField(max_length=2)
    period = models.DateField()
    environment = models.CharField(max_length=20)
    petroleum = models.DecimalField(max_digits=24,decimal_places=8,null=True)
    gas = models.DecimalField(max_digits=24,decimal_places=8,null=True)
    raw = models.JSONField(default=dict)
    snapshot = models.ForeignKey(Snapshot,on_delete=models.PROTECT)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering=['-period','name']
        constraints=[models.UniqueConstraint(fields=['uf','name_key','period'],name='well_production_period')]

class Opportunity(models.Model):
    title = models.CharField('Oportunidade',max_length=240)
    organization = models.ForeignKey(Organization,verbose_name='Organização',on_delete=models.PROTECT,related_name='opportunities')
    signal = models.OneToOneField(Signal,on_delete=models.SET_NULL,null=True,blank=True,related_name='opportunity')
    front = models.CharField('Frente',max_length=30,choices=FRONTS)
    stage = models.CharField('Etapa',max_length=30,choices=STAGES,default='identificada')
    route = models.CharField('Rota',max_length=16,choices=[('definir','A definir'),('direta','Direta'),('nupec','Via NUPEC')],default='definir')
    priority = models.PositiveSmallIntegerField('Prioridade definida por você',choices=[(1,'Alta'),(2,'Normal'),(3,'Baixa')],default=2)
    priority_reason = models.TextField('Justificativa da prioridade',blank=True)
    problem = models.TextField('Problema e evidências',blank=True)
    scope = models.TextField('Escopo e entregas possíveis',blank=True)
    owner = models.CharField('Responsável',max_length=100,default='A definir')
    decision_maker = models.CharField('Decisor ou setor',max_length=180,blank=True)
    technical_ready = models.BooleanField('Capacidade técnica confirmada para este escopo',default=False)
    expected_value = models.DecimalField('Valor estimado da proposta (R$)',max_digits=16,decimal_places=2,null=True,blank=True,validators=[MinValueValidator(0)])
    estimated_cost = models.DecimalField('Custo estimado de execução (R$)',max_digits=16,decimal_places=2,null=True,blank=True,validators=[MinValueValidator(0)])
    expected_receipt = models.DateField('Primeiro recebimento esperado',null=True,blank=True)
    next_action = models.CharField('Próxima ação',max_length=300)
    next_date = models.DateField('Prazo da próxima ação',null=True,blank=True)
    blockers = models.TextField('O que falta para avançar',blank=True)
    outcome_note = models.TextField('Justificativa de suspensão, perda ou conclusão',blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: ordering=['priority','next_date','title']
    def __str__(self):return self.title

class Activity(models.Model):
    opportunity = models.ForeignKey(Opportunity,on_delete=models.CASCADE,related_name='activities')
    kind = models.CharField('Tipo',max_length=20,choices=[('nota','Nota'),('contato','Contato realizado'),('reuniao','Reunião'),('decisao','Decisão'),('proposta','Proposta'),('sistema','Alteração de cadastro')],default='nota')
    text = models.TextField('Registro')
    author = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:ordering=['-created_at']

class CashEntry(models.Model):
    opportunity = models.ForeignKey(Opportunity,verbose_name='Oportunidade',on_delete=models.PROTECT,related_name='cash_entries')
    description = models.CharField('Descrição da parcela',max_length=240)
    kind = models.CharField('Natureza',max_length=20,choices=[('honorarios','Honorários'),('exito','Êxito condicionado'),('outro','Outra receita'),('despesa','Despesa')])
    amount = models.DecimalField('Valor (R$)',max_digits=16,decimal_places=2,validators=[MinValueValidator(Decimal('0.01'))])
    status = models.CharField('Situação',max_length=20,choices=[('prevista','Prevista'),('contratada','Contratada'),('faturada','Faturada'),('realizada','Recebida / paga')],default='prevista')
    due_date = models.DateField('Data prevista')
    received_date = models.DateField('Recebido / pago em',null=True,blank=True)
    evidence = models.TextField('Condição contratual e evidência',blank=True)
    class Meta:ordering=['due_date']
    def clean(self):
        if self.status=='realizada' and (not self.received_date or not self.evidence.strip()):
            raise ValidationError('Para registrar recebimento ou pagamento, informe a data e a evidência.')
        if self.received_date and self.status!='realizada':
            raise ValidationError('Data de realização exige situação Recebida / paga.')

class DirectorPlan(models.Model):
    municipality = models.OneToOneField(Municipality,verbose_name='Município',on_delete=models.PROTECT)
    law = models.CharField('Lei e identificação',max_length=240)
    base_date = models.DateField('Data da instituição ou última revisão integral comprovada')
    source_url = models.URLField('Fonte oficial da lei',max_length=1500,validators=[HTTP_VALIDATOR])
    checked_on = models.DateField('Pesquisa de revisões posteriores realizada em',null=True,blank=True)
    confirmed = models.BooleanField('Conferi a lei e pesquisei revisões integrais posteriores',default=False)
    shorter_due = models.DateField('Prazo local de revisão, se comprovado',null=True,blank=True)
    notes = models.TextField('Evidências, alterações parciais e dúvidas',blank=True)
    class Meta:ordering=['base_date']
    @property
    def reference_due(self):
        if self.shorter_due:return self.shorter_due
        try:return self.base_date.replace(year=self.base_date.year+10)
        except ValueError:return self.base_date.replace(year=self.base_date.year+10,day=28)
    @property
    def review_status(self):
        if not self.confirmed:return 'Data a conferir'
        days=(self.reference_due-date.today()).days
        if days<0:return 'Marco de revisão ultrapassado — verificar situação'
        if days<=365:return 'Revisão a verificar nos próximos 12 meses'
        return 'Marco de revisão futuro'
    def clean(self):
        if self.confirmed and not self.checked_on:raise ValidationError('Informe quando pesquisou revisões posteriores.')
        if self.base_date and self.base_date>date.today():raise ValidationError('A data da lei não pode ser futura.')

class WatchedPage(models.Model):
    format = models.CharField('Formato', max_length=10, default='html', choices=[('html','Página HTML'),('rss','Feed RSS/Atom'),('pdf','PDF com texto')])
    audience = models.CharField('Origem', max_length=15, default='publica', choices=[('publica','Pública/institucional'),('privada','Empresa / oportunidade privada')])
    last_status = models.CharField(max_length=15, blank=True)
    last_error = models.TextField(blank=True)
    last_success_at = models.DateTimeField(null=True, blank=True)
    title=models.CharField('Nome da fonte',max_length=200)
    url=models.URLField('Página pública a acompanhar',max_length=1500,unique=True,validators=[HTTP_VALIDATOR])
    municipality=models.ForeignKey(Municipality,verbose_name='Município',null=True,blank=True,on_delete=models.SET_NULL)
    kind=models.CharField('Finalidade',max_length=20,choices=SIGNAL_KINDS,default='plano')
    keywords=models.CharField('Termos separados por vírgula',max_length=500,default='plano diretor, regularização fundiária, georreferenciamento')
    active=models.BooleanField('Ativa',default=True)
    last_checked=models.DateTimeField(null=True,blank=True)
    last_hash=models.CharField(max_length=64,blank=True)
    class Meta:ordering=['title']

def attachment_path(instance,filename):
    import uuid
    from pathlib import Path
    return f'{instance.opportunity_id}/{uuid.uuid4().hex}{Path(filename).suffix.lower()}'

class Attachment(models.Model):
    opportunity=models.ForeignKey(Opportunity,on_delete=models.CASCADE,related_name='attachments')
    title=models.CharField('Nome e versão do documento',max_length=200)
    file=models.FileField('Arquivo',upload_to=attachment_path)
    created_at=models.DateTimeField(auto_now_add=True)


SCHEDULE_SOURCES = [('pncp_capacidades','PNCP — propostas abertas'),('diarios','Diários municipais — Querido Diário'),
    ('paginas','Páginas e feeds monitorados'),('pocos','ANP — cadastro e localização de poços'),
    ('anp','ANP — royalties do ano atual'),('producao_url','ANP — produção via URL pública de CSV')]

class CollectionSchedule(models.Model):
    name = models.CharField('Nome da rotina', max_length=180)
    seed_key = models.CharField(max_length=80, unique=True, null=True, blank=True)
    source = models.CharField('Coleta', max_length=40, choices=SCHEDULE_SOURCES)
    enabled = models.BooleanField('Ativa', default=True)
    frequency = models.CharField('Repetição', max_length=12, choices=[('interval','A cada intervalo'),('daily','Todo dia'),('weekly','Dia da semana'),('monthly','Dia do mês')], default='weekly')
    interval_minutes = models.PositiveIntegerField('Intervalo em minutos', default=60, validators=[MinValueValidator(15),MaxValueValidator(10080)])
    at_time = models.TimeField('Horário — Brasília/Fortaleza', default='08:00')
    weekday = models.PositiveSmallIntegerField('Dia da semana', default=0, choices=list(enumerate(['Segunda','Terça','Quarta','Quinta','Sexta','Sábado','Domingo'])))
    monthday = models.PositiveSmallIntegerField('Dia do mês', default=20, validators=[MinValueValidator(1),MaxValueValidator(31)])
    parameters = models.JSONField(default=dict, blank=True)
    next_run = models.DateTimeField(null=True, blank=True, db_index=True)
    last_run = models.DateTimeField(null=True, blank=True)
    last_job = models.ForeignKey(CollectionJob, null=True, blank=True, on_delete=models.SET_NULL)
    class Meta:
        ordering = ['next_run','name']

class SchedulerState(models.Model):
    key = models.CharField(max_length=20, primary_key=True, default='local')
    heartbeat = models.DateTimeField(null=True, blank=True)
    message = models.CharField(max_length=300, blank=True)
