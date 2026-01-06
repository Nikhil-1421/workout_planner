"""Tests for export functionality."""

import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4

import pytest

from app.core.export import (
    export_session_csv,
    export_session_csv_string,
    export_session_json,
    export_session_json_string,
    generate_export_filename,
    session_to_dict,
)
from app.core.models import SessionExercise, Set, WorkoutSession


@pytest.fixture
def sample_session():
    """Create a sample workout session for testing."""
    session = WorkoutSession(
        id=uuid4(),
        template_id=uuid4(),
        template_name="Push Day",
        started_at=datetime(2024, 1, 15, 10, 0, 0),
        ended_at=datetime(2024, 1, 15, 11, 30, 0),
        duration_seconds=5400,
        notes=None,
        exercises=[],
    )

    # Add exercises with sets
    exercise1 = SessionExercise(
        id=uuid4(),
        session_id=session.id,
        name="Bench Press",
        order_index=0,
        uses_weight=True,
        sets=[
            Set(
                id=uuid4(),
                session_exercise_id=uuid4(),
                reps=10,
                weight=135.0,
                created_at=datetime(2024, 1, 15, 10, 5, 0),
            ),
            Set(
                id=uuid4(),
                session_exercise_id=uuid4(),
                reps=8,
                weight=145.0,
                created_at=datetime(2024, 1, 15, 10, 8, 0),
            ),
        ],
    )

    exercise2 = SessionExercise(
        id=uuid4(),
        session_id=session.id,
        name="Pull-ups",
        order_index=1,
        uses_weight=False,
        sets=[
            Set(
                id=uuid4(),
                session_exercise_id=uuid4(),
                reps=10,
                weight=None,
                created_at=datetime(2024, 1, 15, 10, 15, 0),
            ),
        ],
    )

    session.exercises = [exercise1, exercise2]
    return session


class TestSessionToDict:
    """Test cases for session_to_dict."""

    def test_basic_conversion(self, sample_session):
        """Should convert session to dictionary."""
        data = session_to_dict(sample_session)

        assert data["session_id"] == str(sample_session.id)
        assert data["template_name"] == "Push Day"
        assert data["duration_seconds"] == 5400

    def test_exercises_included(self, sample_session):
        """Should include exercises in output."""
        data = session_to_dict(sample_session)

        assert len(data["exercises"]) == 2
        assert data["exercises"][0]["name"] == "Bench Press"
        assert data["exercises"][1]["name"] == "Pull-ups"

    def test_sets_included(self, sample_session):
        """Should include sets in exercises."""
        data = session_to_dict(sample_session)

        bench_sets = data["exercises"][0]["sets"]
        assert len(bench_sets) == 2
        assert bench_sets[0]["reps"] == 10
        assert bench_sets[0]["weight"] == 135.0

    def test_summary_calculated(self, sample_session):
        """Should calculate summary stats."""
        data = session_to_dict(sample_session)

        summary = data["summary"]
        assert summary["total_exercises"] == 2
        assert summary["total_sets"] == 3
        assert summary["total_reps"] == 28  # 10 + 8 + 10
        assert summary["total_volume"] == 2510.0  # 135*10 + 145*8

    def test_null_weight_handled(self, sample_session):
        """Should handle null weight (bodyweight exercises)."""
        data = session_to_dict(sample_session)

        pullup_sets = data["exercises"][1]["sets"]
        assert pullup_sets[0]["weight"] is None


class TestExportJson:
    """Test cases for JSON export."""

    def test_export_json_string(self, sample_session):
        """Should export to JSON string."""
        json_str = export_session_json_string(sample_session)
        data = json.loads(json_str)

        assert data["template_name"] == "Push Day"
        assert len(data["exercises"]) == 2

    def test_export_json_file(self, sample_session):
        """Should export to JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test_export.json"
            result = export_session_json(sample_session, filepath)

            assert result == filepath
            assert filepath.exists()

            with open(filepath) as f:
                data = json.load(f)
            assert data["template_name"] == "Push Day"


class TestExportCsv:
    """Test cases for CSV export."""

    def test_export_csv_string(self, sample_session):
        """Should export to CSV string."""
        csv_str = export_session_csv_string(sample_session)
        lines = csv_str.strip().split("\n")

        # Header + 3 sets
        assert len(lines) == 4

        # Check header
        assert lines[0] == "exercise,set_number,reps,weight,created_at"

        # Check first set
        assert "Bench Press,1,10,135.0" in lines[1]

    def test_export_csv_file(self, sample_session):
        """Should export to CSV file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test_export.csv"
            result = export_session_csv(sample_session, filepath)

            assert result == filepath
            assert filepath.exists()

            with open(filepath) as f:
                content = f.read()
            assert "Bench Press" in content
            assert "Pull-ups" in content

    def test_csv_empty_weight(self, sample_session):
        """Should handle empty weight in CSV."""
        csv_str = export_session_csv_string(sample_session)

        # Pull-ups row should have empty weight
        lines = csv_str.strip().split("\n")
        pullup_line = [l for l in lines if "Pull-ups" in l][0]
        assert "Pull-ups,1,10,," in pullup_line


class TestGenerateFilename:
    """Test cases for filename generation."""

    def test_basic_filename(self, sample_session):
        """Should generate filename with date and template."""
        filename = generate_export_filename(sample_session, "json")

        assert filename == "ironlog_Push_Day_2024-01-15.json"

    def test_csv_extension(self, sample_session):
        """Should use correct extension."""
        filename = generate_export_filename(sample_session, "csv")

        assert filename.endswith(".csv")

    def test_custom_workout_name(self):
        """Should handle custom workout without template."""
        session = WorkoutSession(
            id=uuid4(),
            template_id=None,
            template_name=None,
            started_at=datetime(2024, 2, 20, 14, 0, 0),
            ended_at=datetime(2024, 2, 20, 15, 0, 0),
            duration_seconds=3600,
            notes=None,
            exercises=[],
        )

        filename = generate_export_filename(session, "json")
        assert filename == "ironlog_Workout_2024-02-20.json"

    def test_special_characters_sanitized(self):
        """Should sanitize special characters in template name."""
        session = WorkoutSession(
            id=uuid4(),
            template_id=uuid4(),
            template_name="Upper/Lower (Week 1)",
            started_at=datetime(2024, 3, 10, 8, 0, 0),
            ended_at=None,
            duration_seconds=None,
            notes=None,
            exercises=[],
        )

        filename = generate_export_filename(session, "json")
        # Should not contain special characters
        assert "/" not in filename
        assert "(" not in filename
        assert ")" not in filename
