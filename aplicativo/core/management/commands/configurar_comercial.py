from django.core.management.base import BaseCommand
from django.db import transaction
from core.commercial import seed_frente1
from core.collectors import excluded_terms
from core.models import Signal


class Command(BaseCommand):
    help = 'Prepara a lista quente da Frente 1 e aplica o filtro de exclusão aos editais ainda não revisados. Idempotente.'

    @transaction.atomic
    def handle(self, *args, **options):
        created = seed_frente1()
        from core.prospect import seed_prospect
        extra = seed_prospect()
        discarded = 0
        for s in Signal.objects.filter(source_type='pncp', status='novo'):
            hits = excluded_terms(str(s.payload.get('objeto') or s.title))
            if hits:
                s.status = 'descartado'
                s.review_note = 'Triagem automática 0.4.2: objeto é compra de bens ou software (' + ', '.join(hits[:3]) + '), fora do escopo de serviços.'
                s.save(update_fields=['status', 'review_note', 'updated_at'])
                discarded += 1
        self.stdout.write(f'Comercial preparado: {created} alvos novos da Frente 1; {discarded} editais descartados pelo filtro de exclusão. Pesquisa 29/09: {extra}.')
