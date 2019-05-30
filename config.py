import pathlib

PROJECT_DIR = pathlib.Path(__file__).parent
TEMPLATES_DIR = PROJECT_DIR / 'templates'
SOLUTIONS_FOLDER = PROJECT_DIR / 'data' / 'solutions'
DB_PATH = PROJECT_DIR / 'data' / 'storage.db'
TASK_TIMEOUT = 3.0