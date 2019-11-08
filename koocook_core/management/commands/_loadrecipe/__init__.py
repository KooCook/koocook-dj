from django.core.management.base import BaseCommand, CommandError
from koocook_core.models import *
from koocook_core.support import *


def add_datatrans_to_path():
    import sys
    sys.path.insert(0, 'C:\\Users\\User\\PycharmProjects\\datatrans')


class Command(BaseCommand):
    help = 'load recipe data'

    def handle(self, *args, **options):
        self.stdout.write('I was called')
        self.stdout.write('calling read_data')
        add_datatrans_to_path()
        from .read_data import main
        main()

