"""Tests for repository classes."""

import tempfile
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import pytest

from app.core.models import (
    SessionExercise,
    Set,
    TemplateExercise,
    TimerState,
    WorkoutSession,
    WorkoutTemplate,
)
from app.data.db import Database
from app.data.repositories import (
    AppStateRepository,
    SessionRepository,
    TemplateRepository,
)


@pytest.fixture
def db():
    """Create a temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        database = Database(db_path)
        database.initialize()
        yield database
        database.close()


@pytest.fixture
def template_repo(db):
    """Create a template repository."""
    return TemplateRepository(db)


@pytest.fixture
def session_repo(db):
    """Create a session repository."""
    return SessionRepository(db)


@pytest.fixture
def state_repo(db):
    """Create an app state repository."""
    return AppStateRepository(db)


class TestTemplateRepository:
    """Test cases for TemplateRepository."""

    def test_get_all_includes_seeded_templates(self, template_repo):
        """Seeded templates should be present."""
        templates = template_repo.get_all()
        assert len(templates) >= 3  # Push, Pull, Leg
        names = [t.name for t in templates]
        assert "Push Day" in names
        assert "Pull Day" in names
        assert "Leg Day" in names

    def test_create_template(self, template_repo):
        """Should create a new template."""
        template = WorkoutTemplate.create("My Template")
        template_repo.save(template)

        loaded = template_repo.get_by_id(template.id)
        assert loaded is not None
        assert loaded.name == "My Template"

    def test_template_with_exercises(self, template_repo):
        """Should save template with exercises."""
        template = WorkoutTemplate.create("Full Body")
        template.exercises = [
            TemplateExercise.create(template.id, "Squats", 0, True),
            TemplateExercise.create(template.id, "Bench Press", 1, True),
            TemplateExercise.create(template.id, "Pull-ups", 2, False),
        ]
        template_repo.save(template)

        loaded = template_repo.get_by_id(template.id)
        assert len(loaded.exercises) == 3
        assert loaded.exercises[0].name == "Squats"
        assert loaded.exercises[2].uses_weight is False

    def test_update_template(self, template_repo):
        """Should update existing template."""
        template = WorkoutTemplate.create("Original")
        template_repo.save(template)

        template.name = "Updated"
        template_repo.save(template)

        loaded = template_repo.get_by_id(template.id)
        assert loaded.name == "Updated"

    def test_delete_template(self, template_repo):
        """Should delete a template."""
        template = WorkoutTemplate.create("To Delete")
        template_repo.save(template)

        template_repo.delete(template.id)

        loaded = template_repo.get_by_id(template.id)
        assert loaded is None

    def test_duplicate_template(self, template_repo):
        """Should duplicate a template."""
        original = WorkoutTemplate.create("Original")
        original.exercises = [
            TemplateExercise.create(original.id, "Exercise 1", 0, True),
        ]
        template_repo.save(original)

        copy = template_repo.duplicate(original.id, "Copy")

        assert copy is not None
        assert copy.id != original.id
        assert copy.name == "Copy"
        assert len(copy.exercises) == 1
        assert copy.exercises[0].name == "Exercise 1"


class TestSessionRepository:
    """Test cases for SessionRepository."""

    def test_create_session(self, session_repo):
        """Should create a new session."""
        session = WorkoutSession.create()
        session_repo.save(session)

        loaded = session_repo.get_by_id(session.id)
        assert loaded is not None
        assert loaded.is_active

    def test_session_with_exercises(self, session_repo):
        """Should save session with exercises."""
        session = WorkoutSession.create()
        session_repo.save(session)

        exercise = SessionExercise.create(session.id, "Deadlift", 0, True)
        session_repo.save_exercise(exercise)

        loaded = session_repo.get_by_id(session.id)
        assert len(loaded.exercises) == 1
        assert loaded.exercises[0].name == "Deadlift"

    def test_session_with_sets(self, session_repo):
        """Should save exercises with sets."""
        session = WorkoutSession.create()
        session_repo.save(session)

        exercise = SessionExercise.create(session.id, "Bench Press", 0, True)
        session_repo.save_exercise(exercise)

        set1 = Set.create(exercise.id, reps=10, weight=135.0)
        set2 = Set.create(exercise.id, reps=8, weight=145.0)
        session_repo.save_set(set1)
        session_repo.save_set(set2)

        loaded = session_repo.get_by_id(session.id)
        assert len(loaded.exercises[0].sets) == 2
        assert loaded.exercises[0].sets[0].reps == 10
        assert loaded.exercises[0].sets[1].weight == 145.0

    def test_end_session(self, session_repo):
        """Should end a session."""
        session = WorkoutSession.create()
        session_repo.save(session)

        session_repo.end_session(session.id, 3600)  # 1 hour

        loaded = session_repo.get_by_id(session.id)
        assert loaded.ended_at is not None
        assert loaded.duration_seconds == 3600
        assert not loaded.is_active

    def test_get_active_session(self, session_repo):
        """Should get active session."""
        # Create an active session
        active = WorkoutSession.create()
        session_repo.save(active)

        # Create an ended session
        ended = WorkoutSession.create()
        session_repo.save(ended)
        session_repo.end_session(ended.id, 1800)

        # Should return only active session
        result = session_repo.get_active()
        assert result is not None
        assert result.id == active.id

    def test_get_last_weight_for_exercise(self, session_repo):
        """Should get last used weight for an exercise."""
        session = WorkoutSession.create()
        session_repo.save(session)

        exercise = SessionExercise.create(session.id, "Squats", 0, True)
        session_repo.save_exercise(exercise)

        # Add sets with increasing weight
        for weight in [135.0, 155.0, 175.0]:
            s = Set.create(exercise.id, reps=5, weight=weight)
            session_repo.save_set(s)

        last_weight = session_repo.get_last_weight_for_exercise("Squats")
        assert last_weight == 175.0

    def test_delete_set(self, session_repo):
        """Should delete a set."""
        session = WorkoutSession.create()
        session_repo.save(session)

        exercise = SessionExercise.create(session.id, "Curls", 0, True)
        session_repo.save_exercise(exercise)

        s = Set.create(exercise.id, reps=12, weight=25.0)
        session_repo.save_set(s)

        session_repo.delete_set(s.id)

        loaded = session_repo.get_by_id(session.id)
        assert len(loaded.exercises[0].sets) == 0


class TestAppStateRepository:
    """Test cases for AppStateRepository."""

    def test_set_and_get(self, state_repo):
        """Should set and get values."""
        state_repo.set("test_key", "test_value")
        assert state_repo.get("test_key") == "test_value"

    def test_get_missing_key(self, state_repo):
        """Should return None for missing keys."""
        assert state_repo.get("nonexistent") is None

    def test_active_session_id(self, state_repo):
        """Should store and retrieve active session ID."""
        session_id = uuid4()
        state_repo.set_active_session_id(session_id)

        loaded = state_repo.get_active_session_id()
        assert loaded == session_id

    def test_clear_active_session_id(self, state_repo):
        """Should clear active session ID."""
        state_repo.set_active_session_id(uuid4())
        state_repo.set_active_session_id(None)

        assert state_repo.get_active_session_id() is None

    def test_last_template_id(self, state_repo):
        """Should store and retrieve last template ID."""
        template_id = uuid4()
        state_repo.set_last_template_id(template_id)

        loaded = state_repo.get_last_template_id()
        assert loaded == template_id

    def test_timer_state(self, state_repo):
        """Should store and retrieve timer state."""
        state = TimerState(
            is_running=True,
            is_paused=False,
            start_time=datetime.now(),
            pause_time=None,
            accumulated_seconds=120.5,
        )
        state_repo.set_timer_state(state)

        loaded = state_repo.get_timer_state()
        assert loaded.is_running is True
        assert loaded.is_paused is False
        assert loaded.accumulated_seconds == 120.5

    def test_clear_all(self, state_repo):
        """Should clear all state."""
        state_repo.set("key1", "value1")
        state_repo.set("key2", "value2")

        state_repo.clear_all()

        assert state_repo.get("key1") is None
        assert state_repo.get("key2") is None
