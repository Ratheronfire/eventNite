import os
from pathlib import Path


def cwd() -> Path:
    return Path(os.path.abspath(__file__)).parent.parent
