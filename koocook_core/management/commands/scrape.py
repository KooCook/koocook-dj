from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'scrape recipes from aggregate sites'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('source', type=str, help="data source to scrape from, "
                                                     "currently supports 'allrecipes' and 'epicurious'")
        parser.add_argument('num', type=int, help='number of recipes to scrape')
        parser.add_argument('page', type=int, nargs='?', help='optional. page to start scraping from (default=1)')

    def handle(self, *args, **options):
        self.stdout.write('calling _scrape')
        from ._add_path import add_datatrans
        add_datatrans()
        from . import _scrape
        try:
            module = getattr(_scrape, options['source'])
        except AttributeError:
            raise CommandError(f"'source' must be a valid source, not '{options['source']}' (check scrape --help)")
        if options['page']:
            module.main(options['num'], options['page'])
        else:
            module.main(options['num'])
