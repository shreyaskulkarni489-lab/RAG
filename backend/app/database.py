import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# Create SQLAlchemy engine supporting both Postgres and SQLite fallback
db_url = settings.DATABASE_URL
if "sqlite" in db_url:
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
else:
    engine = create_engine(db_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
