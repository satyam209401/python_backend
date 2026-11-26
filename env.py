import os
import socket
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

SERVER_ENV = Path("/www/wwwroot/.env")

is_local = os.name == "nt" or "localhost" in socket.gethostname().lower()

env = BASE_DIR / ".env" if is_local else SERVER_ENV

is_loaded = False
if env.is_file():
    load_dotenv(env, override=True)
    is_loaded = True

