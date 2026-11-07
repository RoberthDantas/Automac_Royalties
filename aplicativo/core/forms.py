from django import forms
from .models import Organization,Contact,Opportunity,Activity,CashEntry,DirectorPlan,WatchedPage,Attachment
from .collectors import DEFAULT_TERMS,UF_CODES

class StyledModelForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for f in self.fields.values():
            if isinstance(f,forms.DateField):
                f.widget=forms.DateInput(format='%Y-%m-%d',attrs={'type':'date'})
            if isinstance(f.widget,forms.Textarea):f.widget.attrs['rows']=3

class OrganizationForm(StyledModelForm):
    class Meta:model=Organization;fields=['name','kind','role','municipality','cnpj','website','source_url','verified_on','address','attributes','notes']
class ContactForm(StyledModelForm):
    class Meta:model=Contact;fields=['organization','name','position','email','phone','source_url','verified_on','do_not_contact','notes']
class OpportunityForm(StyledModelForm):
    class Meta:model=Opportunity;exclude=['signal','created_at','updated_at']
    def clean(self):
        d=super().clean()
        if d.get('stage') in ('suspensa','perdida','concluida') and not d.get('outcome_note'):
            self.add_error('outcome_note','Registre o motivo ou a evidência do resultado.')
        return d
class ActivityForm(StyledModelForm):
    class Meta:model=Activity;fields=['kind','text']
class CashForm(StyledModelForm):
    class Meta:model=CashEntry;exclude=[]
class PlanForm(StyledModelForm):
    class Meta:model=DirectorPlan;exclude=[]
class WatchForm(StyledModelForm):
    class Meta:model=WatchedPage;fields=['title','url','format','audience','municipality','kind','keywords','active']
class AttachmentForm(StyledModelForm):
    class Meta:model=Attachment;fields=['title','file']
    def clean_file(self):
        f=self.cleaned_data['file']
        if f.size>25*1024*1024:raise forms.ValidationError('Limite de 25 MB. Mantenha ortofotos e grandes rasters fora do aplicativo.')
        return f

class CollectionForm(forms.Form):
    source=forms.ChoiceField(label='Fonte',choices=[('ibge','IBGE — municípios dos cinco estados'),('anp','ANP — royalties anuais'),('anp_serie','ANP — série de royalties 2021 até hoje (todos os anos)'),('pocos_referencia','ANP — poços: primeira carga, base verificada 18/09/2026'),('pocos','ANP — poços: atualização online'),('pncp','PNCP — oportunidades por objeto'),('paginas','Páginas oficiais monitoradas')])
    year=forms.IntegerField(label='Ano da tabela ANP',min_value=2021,max_value=2100,required=False)
    uf=forms.ChoiceField(label='UF para o PNCP',choices=[(x,x) for x in UF_CODES],initial='PB')
    mode=forms.ChoiceField(label='Consulta PNCP',choices=[('abertas','Propostas abertas — próximos 30 dias'),('publicacoes','Publicações — últimos 7 dias')])
    pages=forms.IntegerField(label='Limite de páginas PNCP',min_value=1,max_value=40,initial=10,help_text='50 registros por página. O sistema sinaliza cobertura parcial ao atingir este limite.')
    terms=forms.CharField(label='Especialidades no objeto do edital',widget=forms.Textarea(attrs={'rows':3}),initial=DEFAULT_TERMS)

class AssistedSignalForm(forms.Form):
    title=forms.CharField(label='Título ou nome da instituição',max_length=240)
    kind=forms.ChoiceField(label='Tipo',choices=[('contato','Contato institucional'),('plano','Plano diretor'),('edital','Edital'),('outro','Outro gatilho')])
    url=forms.URLField(label='Fonte pública consultada',max_length=1500)
    text=forms.CharField(label='Trecho e evidências encontrados',widget=forms.Textarea(attrs={'rows':5}))

EDITORS={'organizacoes':(Organization,OrganizationForm,'Organização'), 'contatos':(Contact,ContactForm,'Contato'),
         'oportunidades':(Opportunity,OpportunityForm,'Oportunidade'), 'financeiro':(CashEntry,CashForm,'Lançamento financeiro'),
         'planos':(DirectorPlan,PlanForm,'Plano diretor'), 'paginas':(WatchedPage,WatchForm,'Página monitorada')}
