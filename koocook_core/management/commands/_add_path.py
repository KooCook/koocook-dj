import sys
import decouple


class ImproperConfigError(Exception):
    pass


def add_datatrans():
    datatrans_path = decouple.config('DATATRANS_PATH', None)
    if datatrans_path is None:
        raise ImproperConfigError('You must specify DATATRANS_PATH to use this functionality')
    sys.path.insert(0, datatrans_path)
