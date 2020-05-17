import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI") or "sqlite:///" + str(
    Path(".") / "app.db"
)

MAMBU_AUTH_USER = os.getenv("MAMBU_AUTH_USER")
MAMBU_AUTH_PW = os.getenv("MAMBU_AUTH_PW")
