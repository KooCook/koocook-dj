from pathlib import Path
from os import path, mkdir

BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / 'data'
LOGS_DIR = BASE_DIR / 'logs'
if not path.exists(LOGS_DIR):
    mkdir(LOGS_DIR)
TEST_DATA_DIR = DATA_DIR / 'test'
