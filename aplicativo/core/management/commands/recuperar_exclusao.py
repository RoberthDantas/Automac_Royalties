"""Lista ou recupera registros apagados pela tela de exclusão (dados/logs/exclusoes.jsonl)."""
import json
from django.conf import settings
from django.core import serializers
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


class Command(BaseCommand):
    help = 'Sem argumentos: lista as exclusões. Com --numero N: recria os registros da exclusão N (mesmos IDs).'

    def add_arguments(self, parser):
        parser.add_argument('--numero', type=int, help='Número da exclusão, como aparece na lista.')

    def handle(self, *args, **opts):
        path = settings.DATA_DIR / 'logs' / 'exclusoes.jsonl'
        if not path.exists():
            self.stdout.write('Nenhuma exclusão registrada.')
            return
        entries = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]
        if not opts['numero']:
            for i, e in enumerate(entries, 1):
                self.stdout.write(f"{i:>3}. {e['quando']} · {e['usuario']} · {e['tipo']} · {e['registro']} ({len(e['dados'])} registros)")
            self.stdout.write('Para recuperar: manage.py recuperar_exclusao --numero N')
            return
        if not 1 <= opts['numero'] <= len(entries):
            raise CommandError('Número fora da lista.')
        entry = entries[opts['numero'] - 1]
        # Pais antes dos filhos: a ordem gravada é a do coletor do Django (filhos primeiro), então invertemos.
        objects = list(serializers.deserialize('json', json.dumps(list(reversed(entry['dados'])))))
        with transaction.atomic():
            for obj in objects:
                obj.save()
        self.stdout.write(f"Recuperado: {entry['registro']} ({len(objects)} registros). Arquivos anexados apagados do disco não voltam.")
