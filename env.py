import sys
sys.dont_write_bytecode = True

import os
from pathlib import Path
from dotenv import load_dotenv

# Jo path yahan denge, keval wahi load hoga
ENV_PATH = Path(".env")

env = ENV_PATH
is_loaded = False

if env.is_file():
    load_dotenv(dotenv_path=env, override=True)
    is_loaded = True

# Manage __pycache__ via .env (default: True -> no __pycache__)
dont_write = os.getenv("DONT_WRITE_BYTECODE", "true").strip().lower() in ("true", "1", "yes")
sys.dont_write_bytecode = dont_write
if dont_write:
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
else:
    os.environ.pop("PYTHONDONTWRITEBYTECODE", None)
