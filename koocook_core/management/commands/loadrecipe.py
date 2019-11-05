from django.core.management.base import BaseCommand, CommandError
from koocook_core.models import *
from koocook_core.support import *


class Command(BaseCommand):
    help = 'load recipe data'

    def handle(self, *args, **options):
        pass
