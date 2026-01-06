"""Database migrations for IronLog."""

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from app.data.db import Database

# Migration functions - each takes a Database and applies changes
Migration = Callable[["Database"], None]


def migration_001_initial_schema(db: "Database") -> None:
    """Create initial database schema."""
    with db.transaction() as cursor:
        # Workout templates
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS workout_templates (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL
            )
            """
        )

        # Template exercises
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS template_exercises (
                id TEXT PRIMARY KEY,
                template_id TEXT NOT NULL,
                name TEXT NOT NULL,
                order_index INTEGER NOT NULL,
                uses_weight INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (template_id) REFERENCES workout_templates(id) ON DELETE CASCADE
            )
            """
        )

        # Workout sessions
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS workout_sessions (
                id TEXT PRIMARY KEY,
                template_id TEXT,
                template_name TEXT,
                started_at TIMESTAMP NOT NULL,
                ended_at TIMESTAMP,
                duration_seconds INTEGER,
                notes TEXT,
                FOREIGN KEY (template_id) REFERENCES workout_templates(id) ON DELETE SET NULL
            )
            """
        )

        # Session exercises
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS session_exercises (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                name TEXT NOT NULL,
                order_index INTEGER NOT NULL,
                uses_weight INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (session_id) REFERENCES workout_sessions(id) ON DELETE CASCADE
            )
            """
        )

        # Sets
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sets (
                id TEXT PRIMARY KEY,
                session_exercise_id TEXT NOT NULL,
                reps INTEGER NOT NULL,
                weight REAL,
                created_at TIMESTAMP NOT NULL,
                FOREIGN KEY (session_exercise_id) REFERENCES session_exercises(id) ON DELETE CASCADE
            )
            """
        )

        # App state (key-value store)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS app_state (
                key TEXT PRIMARY KEY,
                value TEXT
            )
            """
        )

        # Indexes for common queries
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_template_exercises_template_id
            ON template_exercises(template_id)
            """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_session_exercises_session_id
            ON session_exercises(session_id)
            """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_sets_session_exercise_id
            ON sets(session_exercise_id)
            """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_workout_sessions_started_at
            ON workout_sessions(started_at DESC)
            """
        )


def migration_002_seed_templates(db: "Database") -> None:
    """Seed default workout templates."""
    from datetime import datetime
    from uuid import uuid4

    templates = [
        {
            "name": "Push Day",
            "exercises": [
                ("Bench Press", True),
                ("Overhead Press", True),
                ("Incline Dumbbell Press", True),
                ("Tricep Pushdowns", True),
                ("Lateral Raises", True),
            ],
        },
        {
            "name": "Pull Day",
            "exercises": [
                ("Deadlift", True),
                ("Barbell Rows", True),
                ("Pull-ups", False),
                ("Face Pulls", True),
                ("Bicep Curls", True),
            ],
        },
        {
            "name": "Leg Day",
            "exercises": [
                ("Squats", True),
                ("Romanian Deadlifts", True),
                ("Leg Press", True),
                ("Leg Curls", True),
                ("Calf Raises", True),
            ],
        },
    ]

    with db.transaction() as cursor:
        for template_data in templates:
            template_id = str(uuid4())
            cursor.execute(
                """
                INSERT INTO workout_templates (id, name, created_at)
                VALUES (?, ?, ?)
                """,
                (template_id, template_data["name"], datetime.now()),
            )

            for order_idx, (name, uses_weight) in enumerate(template_data["exercises"]):
                exercise_id = str(uuid4())
                cursor.execute(
                    """
                    INSERT INTO template_exercises (id, template_id, name, order_index, uses_weight)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (exercise_id, template_id, name, order_idx, 1 if uses_weight else 0),
                )


# List of all migrations in order
MIGRATIONS: list[tuple[int, str, Migration]] = [
    (1, "initial_schema", migration_001_initial_schema),
    (2, "seed_templates", migration_002_seed_templates),
]


def get_current_version(db: "Database") -> int:
    """
    Get the current schema version.

    Args:
        db: Database instance

    Returns:
        Current schema version (0 if not initialized)
    """
    with db.cursor() as cursor:
        # Check if schema_version table exists
        cursor.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='schema_version'
            """
        )
        if cursor.fetchone() is None:
            return 0

        cursor.execute("SELECT version FROM schema_version ORDER BY version DESC LIMIT 1")
        row = cursor.fetchone()
        return row["version"] if row else 0


def apply_migrations(db: "Database") -> None:
    """
    Apply all pending migrations.

    Args:
        db: Database instance
    """
    # Ensure schema_version table exists
    with db.transaction() as cursor:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                applied_at TIMESTAMP NOT NULL
            )
            """
        )

    current_version = get_current_version(db)

    for version, name, migration_fn in MIGRATIONS:
        if version > current_version:
            print(f"Applying migration {version}: {name}")
            try:
                migration_fn(db)
                with db.transaction() as cursor:
                    from datetime import datetime

                    cursor.execute(
                        "INSERT INTO schema_version (version, applied_at) VALUES (?, ?)",
                        (version, datetime.now()),
                    )
                print(f"  ✓ Migration {version} applied successfully")
            except Exception as e:
                print(f"  ✗ Migration {version} failed: {e}")
                raise
