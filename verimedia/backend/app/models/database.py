import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Use DATABASE_URL env var (set by Render Postgres) or fall back to local SQLite
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    # Render provides postgres:// but SQLAlchemy 2.x requires postgresql://
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URL = DATABASE_URL
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
else:
    # Local development: use SQLite
    _storage_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "storage")
    os.makedirs(_storage_dir, exist_ok=True)
    _db_path = os.path.join(_storage_dir, "verimedia.db")
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{_db_path}"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

