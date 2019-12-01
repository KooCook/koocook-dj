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
        source = options['source'][0]
        count = 0
        urls = getattr(_scrape, source).get_links('https://www.allrecipes.com/recipes/78/breakfast-and-brunch/')
        while count < options['num'][0]:
            links = getattr(_scrape, source).main(urls.pop(-1))
            count += 1
