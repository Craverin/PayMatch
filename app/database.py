from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import get_database_url

engine = create_engine(get_database_url(), connect_args={"connect_timeout": 10})
SessionFactory = sessionmaker(bind=engine)
