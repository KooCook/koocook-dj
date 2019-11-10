from django.core.management.base import BaseCommand, CommandError


def add_datatrans_to_path():
    import sys
    sys.path.insert(0, 'C:\\Users\\User\\PycharmProjects\\datatrans')


class Command(BaseCommand):
    help = 'load recipe data'

    def handle(self, *args, **options):
        self.stdout.write('calling loadingr')
        add_datatrans_to_path()
        from .load_ingredient import main
        main()

