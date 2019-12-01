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
        count = 0
        i = 0
        urls = module.get_links(f'https://www.allrecipes.com/{f"?page={i + 1}" if i else ""}')
        while count < options['num'][0]:
            try:
                module.main(urls.pop(-1))
            except IndexError:
                i += 1
                urls = module.get_links(f'https://www.allrecipes.com/{f"?page={i + 1}" if i else ""}')
                module.main(urls.pop(-1))
            count += 1
