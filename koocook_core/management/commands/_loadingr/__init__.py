from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'load recipe data'

    def handle(self, *args, **options):
        self.stdout.write('calling loadingr')
        from .._add_path import add_datatrans
        add_datatrans()
        from .load_ingredient import main
        main()

