from decimal import Decimal
from django import template
register=template.Library()
@register.filter
def brl(value):
    if value is None:return 'Não informado'
    text=f'{Decimal(value):,.2f}'.replace(',','_').replace('.',',').replace('_','.')
    return 'R$ '+text
@register.filter
def pct(value):return '—' if value is None else str(round(value,1)).replace('.',',')+'%'
