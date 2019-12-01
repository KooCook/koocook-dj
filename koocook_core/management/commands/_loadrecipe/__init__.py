from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'load recipe data'

    def handle(self, *args, **options):
        self.stdout.write('calling read_data')
        from .._add_path import add_datatrans
        add_datatrans()
        from .main import main
        main()
