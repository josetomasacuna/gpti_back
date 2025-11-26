import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# cargar variables .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# motor síncrono
engine = create_engine(
    DATABASE_URL,
    echo=True
)

# sesión síncrona
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# modelo base
Base = declarative_base()

# dependencia para obtener una sesión por request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
