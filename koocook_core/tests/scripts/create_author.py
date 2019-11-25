from koocook_core.tests import utils
from koocook_core.models import Author
from django.contrib.auth.models import User


def main(*args):
    if args:
        n = args[0]
    else:
        n = 2

    for _ in range(n):
        Author.objects.create(name=utils.get_first_name())
    for _ in range(n):
        Author.objects.create(name=utils.get_last_name())
    for _ in range(n):
        Author.objects.create(name=utils.get_full_name())
    for _ in range(n):
        User.objects.create(username=utils.gen_username(utils.get_first_name(), utils.get_last_name()))
    for _ in range(n):
        f = utils.get_first_name()
        l = utils.get_last_name()
        User.objects.create(username=utils.gen_username(f, l), email=f + l + '@gmail.com')
    for _ in range(n):
        f = utils.get_first_name()
        l = utils.get_last_name()
        User.objects.create(first_name=f, username=utils.gen_username(f, l), email=f + l + '@gmail.com')
    for _ in range(n):
        f = utils.get_first_name()
        l = utils.get_last_name()
        User.objects.create(last_name=l, username=utils.gen_username(f, l), email=f + l + '@gmail.com')
    for _ in range(n):
        f = utils.get_first_name()
        l = utils.get_last_name()
        User.objects.create(first_name=f, last_name=l, username=utils.gen_username(f, l), email=f + l + '@gmail.com')
    for _ in range(n):
        f = utils.get_first_name()
        l = utils.get_last_name()
        User.objects.create(first_name=f, username=utils.gen_username(f, l))
    for _ in range(n):
        f = utils.get_first_name()
        l = utils.get_last_name()
        User.objects.create(last_name=l, username=utils.gen_username(f, l))
    for _ in range(n):
        f = utils.get_first_name()
        l = utils.get_last_name()
        User.objects.create(first_name=f, last_name=l, username=utils.gen_username(f, l))
