import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import URL


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

SHOP_BASE_URL = os.environ["SHOP_BASE_URL"]
STRIPE_BASE_URL = os.environ["STRIPE_BASE_URL"]
STRIPE_API_KEY = os.environ["STRIPE_API_KEY"]
HTTP_REQUEST_TIMEOUT = int(os.environ["HTTP_REQUEST_TIMEOUT"])


def get_database_url() -> URL:
    return URL.create(
        drivername="postgresql+psycopg",
        username=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        host=os.environ["POSTGRES_HOST"],
        port=int(os.environ["POSTGRES_PORT"]),
        database=os.environ["POSTGRES_DB"]
    )

