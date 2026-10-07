from app.config import get_database_url

from alembic import context
from sqlalchemy import create_engine, pool


engine = create_engine(get_database_url(), poolclass=pool.NullPool)

with engine.connect() as connection:
    context.configure(connection=connection)

    with context.begin_transaction():
        context.run_migrations()
