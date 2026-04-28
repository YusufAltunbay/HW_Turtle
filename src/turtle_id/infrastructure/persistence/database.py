"""
Veritabanı bağlantı yönetimi.

SQLAlchemy engine ve session factory'yi tek yerden sağlar.
Uygulama ayağa kalkarken bir kez init_db() çağrılır.
"""
from __future__ import annotations

from pathlib import Path

from loguru import logger
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    """Tüm ORM modellerinin türeyeceği temel sınıf."""


def _enable_wal_mode(dbapi_connection, _connection_record) -> None:
    """SQLite WAL modunu etkinleştir — eş zamanlı okuma/yazma için."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def build_engine(db_path: str | Path = "data/turtle_db.sqlite") -> Engine:
    """
    SQLite engine oluştur.

    Args:
        db_path: Veritabanı dosyasının yolu.

    Returns:
        Yapılandırılmış SQLAlchemy Engine.
    """
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    url = f"sqlite:///{path.as_posix()}"
    engine = create_engine(url, echo=False, future=True)

    event.listen(engine, "connect", _enable_wal_mode)

    logger.info(f"Veritabanı engine oluşturuldu: {path}")
    return engine


def build_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Session factory üret."""
    return sessionmaker(bind=engine, autocommit=False, autoflush=False)


def init_db(engine: Engine) -> None:
    """
    Veritabanı tablolarını oluştur (yoksa).
    Uygulama başlangıcında bir kez çağrılır.
    """
    from turtle_id.infrastructure.persistence import models as _  # noqa: F401 — ORM kayıt için import
    Base.metadata.create_all(engine)
    logger.info("Veritabanı tabloları hazır.")
