from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Utiliser SQLite - Pas besoin de PostgreSQL
DATABASE_URL = "sqlite:///./jobminer.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Nécessaire pour SQLite
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialiser la base de données - créer toutes les tables"""
    Base.metadata.create_all(bind=engine)