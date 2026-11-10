import os
import time

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import declarative_base, sessionmaker

# Read database connection details from environment variables so the same
# code works locally, in Docker Compose and in Kubernetes.
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "doctordb")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db(retries: int = 30, delay: int = 3) -> bool:
    """Create all tables, retrying until Postgres is reachable.

    This is self-healing: it is idempotent (create_all only creates missing
    tables) so it can be safely called at startup and again any time the
    database might have been reset.
    """
    for attempt in range(1, retries + 1):
        try:
            Base.metadata.create_all(bind=engine)
            print("[doctor-service] Database tables ready.")
            return True
        except OperationalError:
            print(f"[doctor-service] DB not ready, retrying... ({attempt}/{retries})")
            time.sleep(delay)
    print("[doctor-service] WARNING: database still not ready after retries.")
    return False


def get_db():
    """FastAPI dependency that yields a database session.

    Self-heals: if the underlying tables have gone missing (e.g. the Postgres
    pod was restarted), it recreates them transparently before serving.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

