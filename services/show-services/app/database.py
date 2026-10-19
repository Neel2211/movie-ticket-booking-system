import os

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


def make_engine(database_url: str):
    kwargs = {"connect_args": {"check_same_thread": False}}

    # Keep one shared connection for an in-memory SQLite database in tests.
    if database_url in ("sqlite://", "sqlite:///:memory:"):
        kwargs["poolclass"] = StaticPool

    engine = create_engine(database_url, **kwargs)

    if database_url.startswith("sqlite"):
        @event.listens_for(engine, "connect")
        def set_sqlite_pragmas(connection, _):
            cursor = connection.cursor()
            cursor.execute("PRAGMA busy_timeout=5000")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


def make_session_factory(engine):
    return sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )


def get_database_url() -> str:
    return os.getenv(
        "SHOW_DATABASE_URL",
        "sqlite:///./show.db",
    )