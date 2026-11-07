from django import forms
from django.core.validators import URLValidator
from .forms import StyledModelForm
from .models import CollectionSchedule

class ScheduleForm(StyledModelForm):
    ufs=forms.MultipleChoiceField(label='UFs do radar',choices=[(x,x) for x in ['PB','RN','CE','SE','AL']],initial=['PB','RN','CE','SE','AL'],required=False,widget=forms.CheckboxSelectMultiple)
    url=forms.URLField(label='URL pública do CSV de produção (somente para essa coleta)',required=False)
    environment=forms.ChoiceField(label='Ambiente do CSV',choices=[('Terra','Terra'),('Mar','Mar')],required=False)
    class Meta:
        model=CollectionSchedule
        fields=['name','source','enabled','frequency','interval_minutes','at_time','weekday','monthday']
        widgets={'at_time':forms.TimeInput(format='%H:%M',attrs={'type':'time'})}
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        if self.instance.pk:
            p=self.instance.parameters or {}
            for key in ('ufs','url','environment'):
                if key in p:self.initial[key]=p[key]
        self.fields['monthday'].help_text='Meses sem esse dia usam o último dia do mês. Horários em Brasília/Fortaleza.'
        self.fields['interval_minutes'].help_text='Intervalo mínimo: 15 minutos. Fontes podem publicar com atraso.'
    def clean(self):
        d=super().clean()
        if d.get('source') in ('pncp_capacidades','diarios') and not d.get('ufs'):self.add_error('ufs','Selecione pelo menos uma UF.')
        if d.get('source')=='producao_url' and not d.get('url'):self.add_error('url','Informe uma URL pública direta do CSV. O portal CDP interativo não é um CSV.')
        return d
