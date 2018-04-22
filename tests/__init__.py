from pathlib import Path

from dotenv import load_dotenv

load_dotenv(verbose=True, dotenv_path=Path('tests/.env'))
