"""Repository classes for data access."""

import json
from datetime import datetime
from typing import Optional
from uuid import UUID

from app.core.models import (
    SessionExercise,
    Set,
    TemplateExercise,
    TimerState,
    WorkoutSession,
    WorkoutTemplate,
)
from app.data.db import Database


class TemplateRepository:
    """Repository for workout template operations."""

    def __init__(self, db: Database) -> None:
        self.db = db

    def get_all(self) -> list[WorkoutTemplate]:
        """Get all workout templates with their exercises."""
        templates: list[WorkoutTemplate] = []

        with self.db.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, name, created_at
                FROM workout_templates
                ORDER BY name
                """
            )
            template_rows = cursor.fetchall()

            for row in template_rows:
                template = WorkoutTemplate(
                    id=UUID(row["id"]),
                    name=row["name"],
                    created_at=row["created_at"],
                    exercises=[],
                )

                # Fetch exercises for this template
                cursor.execute(
                    """
                    SELECT id, template_id, name, order_index, uses_weight
                    FROM template_exercises
                    WHERE template_id = ?
                    ORDER BY order_index
                    """,
                    (str(template.id),),
                )
                for ex_row in cursor.fetchall():
                    template.exercises.append(
                        TemplateExercise(
                            id=UUID(ex_row["id"]),
                            template_id=UUID(ex_row["template_id"]),
                            name=ex_row["name"],
                            order_index=ex_row["order_index"],
                            uses_weight=bool(ex_row["uses_weight"]),
                        )
                    )

                templates.append(template)

        return templates

    def get_by_id(self, template_id: UUID) -> Optional[WorkoutTemplate]:
        """Get a template by ID."""
        with self.db.cursor() as cursor:
            cursor.execute(
                "SELECT id, name, created_at FROM workout_templates WHERE id = ?",
                (str(template_id),),
            )
            row = cursor.fetchone()
            if row is None:
                return None

            template = WorkoutTemplate(
                id=UUID(row["id"]),
                name=row["name"],
                created_at=row["created_at"],
                exercises=[],
            )

            cursor.execute(
                """
                SELECT id, template_id, name, order_index, uses_weight
                FROM template_exercises
                WHERE template_id = ?
                ORDER BY order_index
                """,
                (str(template_id),),
            )
            for ex_row in cursor.fetchall():
                template.exercises.append(
                    TemplateExercise(
                        id=UUID(ex_row["id"]),
                        template_id=UUID(ex_row["template_id"]),
                        name=ex_row["name"],
                        order_index=ex_row["order_index"],
                        uses_weight=bool(ex_row["uses_weight"]),
                    )
                )

            return template

    def save(self, template: WorkoutTemplate) -> None:
        """Save a template (insert or update)."""
        with self.db.transaction() as cursor:
            # Upsert template
            cursor.execute(
                """
                INSERT INTO workout_templates (id, name, created_at)
                VALUES (?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET name = excluded.name
                """,
                (str(template.id), template.name, template.created_at),
            )

            # Delete existing exercises and re-insert
            cursor.execute(
                "DELETE FROM template_exercises WHERE template_id = ?",
                (str(template.id),),
            )

            for exercise in template.exercises:
                cursor.execute(
                    """
                    INSERT INTO template_exercises (id, template_id, name, order_index, uses_weight)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        str(exercise.id),
                        str(template.id),
                        exercise.name,
                        exercise.order_index,
                        1 if exercise.uses_weight else 0,
                    ),
                )

    def delete(self, template_id: UUID) -> None:
        """Delete a template by ID."""
        with self.db.transaction() as cursor:
            cursor.execute(
                "DELETE FROM workout_templates WHERE id = ?",
                (str(template_id),),
            )

    def duplicate(self, template_id: UUID, new_name: str) -> Optional[WorkoutTemplate]:
        """Duplicate a template with a new name."""
        original = self.get_by_id(template_id)
        if original is None:
            return None

        new_template = WorkoutTemplate.create(new_name)
        for ex in original.exercises:
            new_ex = TemplateExercise.create(
                template_id=new_template.id,
                name=ex.name,
                order_index=ex.order_index,
                uses_weight=ex.uses_weight,
            )
            new_template.exercises.append(new_ex)

        self.save(new_template)
        return new_template


class SessionRepository:
    """Repository for workout session operations."""

    def __init__(self, db: Database) -> None:
        self.db = db

    def get_all(self, limit: int = 50) -> list[WorkoutSession]:
        """Get all sessions, newest first."""
        sessions: list[WorkoutSession] = []

        with self.db.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, template_id, template_name, started_at, ended_at,
                       duration_seconds, notes
                FROM workout_sessions
                ORDER BY started_at DESC
                LIMIT ?
                """,
                (limit,),
            )

            for row in cursor.fetchall():
                session = self._row_to_session(row)
                self._load_exercises(cursor, session)
                sessions.append(session)

        return sessions

    def get_by_id(self, session_id: UUID) -> Optional[WorkoutSession]:
        """Get a session by ID with all exercises and sets."""
        with self.db.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, template_id, template_name, started_at, ended_at,
                       duration_seconds, notes
                FROM workout_sessions
                WHERE id = ?
                """,
                (str(session_id),),
            )
            row = cursor.fetchone()
            if row is None:
                return None

            session = self._row_to_session(row)
            self._load_exercises(cursor, session)
            return session

    def get_active(self) -> Optional[WorkoutSession]:
        """Get the current active session (if any)."""
        with self.db.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, template_id, template_name, started_at, ended_at,
                       duration_seconds, notes
                FROM workout_sessions
                WHERE ended_at IS NULL
                ORDER BY started_at DESC
                LIMIT 1
                """
            )
            row = cursor.fetchone()
            if row is None:
                return None

            session = self._row_to_session(row)
            self._load_exercises(cursor, session)
            return session

    def _row_to_session(self, row) -> WorkoutSession:  # noqa: ANN001
        """Convert a database row to a WorkoutSession."""
        return WorkoutSession(
            id=UUID(row["id"]),
            template_id=UUID(row["template_id"]) if row["template_id"] else None,
            template_name=row["template_name"],
            started_at=row["started_at"],
            ended_at=row["ended_at"],
            duration_seconds=row["duration_seconds"],
            notes=row["notes"],
            exercises=[],
        )

    def _load_exercises(self, cursor, session: WorkoutSession) -> None:  # noqa: ANN001
        """Load exercises and sets for a session."""
        cursor.execute(
            """
            SELECT id, session_id, name, order_index, uses_weight
            FROM session_exercises
            WHERE session_id = ?
            ORDER BY order_index
            """,
            (str(session.id),),
        )

        for ex_row in cursor.fetchall():
            exercise = SessionExercise(
                id=UUID(ex_row["id"]),
                session_id=UUID(ex_row["session_id"]),
                name=ex_row["name"],
                order_index=ex_row["order_index"],
                uses_weight=bool(ex_row["uses_weight"]),
                sets=[],
            )

            # Load sets for this exercise
            cursor.execute(
                """
                SELECT id, session_exercise_id, reps, weight, created_at
                FROM sets
                WHERE session_exercise_id = ?
                ORDER BY created_at
                """,
                (str(exercise.id),),
            )

            for set_row in cursor.fetchall():
                exercise.sets.append(
                    Set(
                        id=UUID(set_row["id"]),
                        session_exercise_id=UUID(set_row["session_exercise_id"]),
                        reps=set_row["reps"],
                        weight=set_row["weight"],
                        created_at=set_row["created_at"],
                    )
                )

            session.exercises.append(exercise)

    def save(self, session: WorkoutSession) -> None:
        """Save a session (insert or update)."""
        with self.db.transaction() as cursor:
            cursor.execute(
                """
                INSERT INTO workout_sessions
                    (id, template_id, template_name, started_at, ended_at, duration_seconds, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    template_id = excluded.template_id,
                    template_name = excluded.template_name,
                    ended_at = excluded.ended_at,
                    duration_seconds = excluded.duration_seconds,
                    notes = excluded.notes
                """,
                (
                    str(session.id),
                    str(session.template_id) if session.template_id else None,
                    session.template_name,
                    session.started_at,
                    session.ended_at,
                    session.duration_seconds,
                    session.notes,
                ),
            )

    def save_exercise(self, exercise: SessionExercise) -> None:
        """Save an exercise within a session."""
        with self.db.transaction() as cursor:
            cursor.execute(
                """
                INSERT INTO session_exercises (id, session_id, name, order_index, uses_weight)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    order_index = excluded.order_index,
                    uses_weight = excluded.uses_weight
                """,
                (
                    str(exercise.id),
                    str(exercise.session_id),
                    exercise.name,
                    exercise.order_index,
                    1 if exercise.uses_weight else 0,
                ),
            )

    def delete_exercise(self, exercise_id: UUID) -> None:
        """Delete an exercise from a session."""
        with self.db.transaction() as cursor:
            cursor.execute(
                "DELETE FROM session_exercises WHERE id = ?",
                (str(exercise_id),),
            )

    def save_set(self, workout_set: Set) -> None:
        """Save a set within an exercise."""
        with self.db.transaction() as cursor:
            cursor.execute(
                """
                INSERT INTO sets (id, session_exercise_id, reps, weight, created_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    reps = excluded.reps,
                    weight = excluded.weight
                """,
                (
                    str(workout_set.id),
                    str(workout_set.session_exercise_id),
                    workout_set.reps,
                    workout_set.weight,
                    workout_set.created_at,
                ),
            )

    def delete_set(self, set_id: UUID) -> None:
        """Delete a set."""
        with self.db.transaction() as cursor:
            cursor.execute("DELETE FROM sets WHERE id = ?", (str(set_id),))

    def end_session(self, session_id: UUID, duration_seconds: int) -> None:
        """Mark a session as ended."""
        with self.db.transaction() as cursor:
            cursor.execute(
                """
                UPDATE workout_sessions
                SET ended_at = ?, duration_seconds = ?
                WHERE id = ?
                """,
                (datetime.now(), duration_seconds, str(session_id)),
            )

    def delete(self, session_id: UUID) -> None:
        """Delete a session."""
        with self.db.transaction() as cursor:
            cursor.execute(
                "DELETE FROM workout_sessions WHERE id = ?",
                (str(session_id),),
            )

    def get_last_weight_for_exercise(self, exercise_name: str) -> Optional[float]:
        """Get the last used weight for an exercise across all sessions."""
        with self.db.cursor() as cursor:
            cursor.execute(
                """
                SELECT s.weight
                FROM sets s
                JOIN session_exercises se ON s.session_exercise_id = se.id
                WHERE se.name = ? AND s.weight IS NOT NULL
                ORDER BY s.created_at DESC
                LIMIT 1
                """,
                (exercise_name,),
            )
            row = cursor.fetchone()
            return row["weight"] if row else None


class AppStateRepository:
    """Repository for application state."""

    def __init__(self, db: Database) -> None:
        self.db = db

    def get(self, key: str) -> Optional[str]:
        """Get a state value by key."""
        with self.db.cursor() as cursor:
            cursor.execute("SELECT value FROM app_state WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row["value"] if row else None

    def set(self, key: str, value: str) -> None:
        """Set a state value."""
        with self.db.transaction() as cursor:
            cursor.execute(
                """
                INSERT INTO app_state (key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (key, value),
            )

    def delete(self, key: str) -> None:
        """Delete a state value."""
        with self.db.transaction() as cursor:
            cursor.execute("DELETE FROM app_state WHERE key = ?", (key,))

    def get_active_session_id(self) -> Optional[UUID]:
        """Get the active session ID."""
        value = self.get("active_session_id")
        return UUID(value) if value else None

    def set_active_session_id(self, session_id: Optional[UUID]) -> None:
        """Set the active session ID."""
        if session_id is None:
            self.delete("active_session_id")
        else:
            self.set("active_session_id", str(session_id))

    def get_last_template_id(self) -> Optional[UUID]:
        """Get the last used template ID."""
        value = self.get("last_template_id")
        return UUID(value) if value else None

    def set_last_template_id(self, template_id: Optional[UUID]) -> None:
        """Set the last used template ID."""
        if template_id is None:
            self.delete("last_template_id")
        else:
            self.set("last_template_id", str(template_id))

    def get_timer_state(self) -> Optional[TimerState]:
        """Get the persisted timer state."""
        value = self.get("timer_state")
        if value is None:
            return None

        try:
            data = json.loads(value)
            return TimerState(
                is_running=data["is_running"],
                is_paused=data["is_paused"],
                start_time=(
                    datetime.fromisoformat(data["start_time"])
                    if data["start_time"]
                    else None
                ),
                pause_time=(
                    datetime.fromisoformat(data["pause_time"])
                    if data["pause_time"]
                    else None
                ),
                accumulated_seconds=data["accumulated_seconds"],
            )
        except (json.JSONDecodeError, KeyError):
            return None

    def set_timer_state(self, state: Optional[TimerState]) -> None:
        """Set the timer state."""
        if state is None:
            self.delete("timer_state")
        else:
            data = {
                "is_running": state.is_running,
                "is_paused": state.is_paused,
                "start_time": state.start_time.isoformat() if state.start_time else None,
                "pause_time": state.pause_time.isoformat() if state.pause_time else None,
                "accumulated_seconds": state.accumulated_seconds,
            }
            self.set("timer_state", json.dumps(data))

    def clear_all(self) -> None:
        """Clear all app state (for reset)."""
        with self.db.transaction() as cursor:
            cursor.execute("DELETE FROM app_state")
