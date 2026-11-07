import json
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Municipality, Signal, InternalPlan, InternalPlanLog

class Command(BaseCommand):
    help = 'Carga local idempotente: municípios e planejamento. Preserva cadastros e decisões existentes.'

    @transaction.atomic
    def handle(self, *args, **options):
        root = settings.BASE_DIR / 'referencias'
        catalog = json.loads((root/'cartografia_20260921/municipios.json').read_text(encoding='utf-8'))
        n = 0
        for row in catalog:
            code = row.pop('code')
            _, created = Municipality.objects.get_or_create(code=code, defaults=row)
            n += created
        cabedelo = Municipality.objects.get(pk='2503209')
        actions = json.loads((root/'planejamento_20260921/acoes.json').read_text(encoding='utf-8'))
        added = 0
        for a in actions:
            signal, _ = Signal.objects.get_or_create(external_key=a['key'], defaults={
                'title':a['title'], 'kind':a['kind'], 'municipality':cabedelo,
                'source_url':a['url'], 'reason':a['reason'], 'payload':a})
            plan, created = InternalPlan.objects.get_or_create(seed_key=a['key'], defaults={
                'title':a['title'], 'category':a['kind'], 'signal':signal, 'municipality':cabedelo,
                'next_action':a['next'], 'blockers':a['blockers']})
            if created:
                InternalPlanLog.objects.create(plan=plan,author='Carga inicial',changes={'criado':a['title']})
                added += 1
        self.stdout.write(f'Configuração: {n} municípios novos; {added} ações internas novas. Registros existentes preservados.')
