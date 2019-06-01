import pathlib
import os

PROJECT_DIR = pathlib.Path(__file__).parent
TEMPLATES_DIR = PROJECT_DIR / 'templates'
SOLUTIONS_FOLDER = PROJECT_DIR / 'data' / 'solutions'
DB_NAME = 'storage.db'
TASK_TIMEOUT = 3.0
locals().update(**{k.split('_', 1)[1]: v for k, v in os.environ.items() if k.startswith('APP_')})

DB_PATH = PROJECT_DIR / 'data' / DB_NAME
