from django.core.management.base import BaseCommand
from core.importer import import_folder


class Command(BaseCommand):
    help = 'Importa royalties (.xlsx) e produção por poço (.csv) colocados em dados/importar. Cada arquivo uma única vez.'

    def handle(self, *args, **options):
        results = import_folder()
        self.stdout.write('Pasta importar: ' + ('; '.join(results) if results else 'nenhum arquivo novo.'))
