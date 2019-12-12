from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'scrape recipes from allrecipes'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('source', nargs='+', type=str)
        parser.add_argument('num', nargs='+', type=int)

    def handle(self, *args, **options):
        self.stdout.write('calling _scrape')
        from ._add_path import add_datatrans
        add_datatrans()
        from . import _scrape
        module = getattr(_scrape, options['source'][0])
        module.main(options['num'][0])
