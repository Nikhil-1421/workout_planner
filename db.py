"""SQLite database connection and management."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional

from app.data.migrations import apply_migrations


class Database:
    """
    SQLite database connection manager.

    Provides thread-safe database access with automatic migrations.
    """

    _instance: Optional["Database"] = None

    def __init__(self, db_path: Optional[Path] = None) -> None:
        """
        Initialize the database.

        Args:
            db_path: Path to the database file. If None, uses default location.
        """
        if db_path is None:
            # Default to user's home directory
            db_path = Path.home() / ".ironlog" / "ironlog.db"

        self.db_path = db_path
        self._ensure_directory()
        self._connection: Optional[sqlite3.Connection] = None

    def _ensure_directory(self) -> None:
        """Ensure the database directory exists."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_instance(cls, db_path: Optional[Path] = None) -> "Database":
        """
        Get the singleton database instance.

        Args:
            db_path: Path to database file (only used on first call)

        Returns:
            The database instance
        """
        if cls._instance is None:
            cls._instance = cls(db_path)
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton instance. For testing only."""
        if cls._instance is not None:
            cls._instance.close()
            cls._instance = None

    def connect(self) -> sqlite3.Connection:
        """
        Get a database connection.

        Returns:
            SQLite connection object
        """
        if self._connection is None:
            self._connection = sqlite3.connect(
                str(self.db_path),
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
                check_same_thread=False,
            )
            # Enable foreign keys
            self._connection.execute("PRAGMA foreign_keys = ON")
            # Use WAL mode for better concurrent access
            self._connection.execute("PRAGMA journal_mode = WAL")
            # Row factory for dict-like access
            self._connection.row_factory = sqlite3.Row

        return self._connection

    def close(self) -> None:
        """Close the database connection."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Cursor, None, None]:
        """
        Context manager for database transactions.

        Yields:
            A cursor for executing queries

        Raises:
            Exception: Re-raises any exception after rollback
        """
        conn = self.connect()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()

    @contextmanager
    def cursor(self) -> Generator[sqlite3.Cursor, None, None]:
        """
        Context manager for read-only queries.

        Yields:
            A cursor for executing queries
        """
        conn = self.connect()
        cursor = conn.cursor()
        try:
            yield cursor
        finally:
            cursor.close()

    def initialize(self) -> None:
        """
        Initialize the database with schema and migrations.

        Should be called once at app startup.
        """
        apply_migrations(self)

    def reset(self) -> None:
        """
        Reset the database by deleting all data.

        WARNING: This is destructive and cannot be undone.
        """
        self.close()
        if self.db_path.exists():
            self.db_path.unlink()
        self._ensure_directory()
        self.initialize()


def get_db() -> Database:
    """
    Get the database instance.

    Returns:
        The singleton database instance
    """
    return Database.get_instance()
