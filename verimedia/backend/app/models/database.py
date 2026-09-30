import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Use STORAGE_DIR env var (set on Render) or fall back to local relative path
_storage_dir = os.environ.get("STORAGE_DIR", os.path.join(os.path.dirname(__file__), "..", "..", "..", "storage"))
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
