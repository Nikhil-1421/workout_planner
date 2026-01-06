"""Export functionality for workout sessions."""

import csv
import json
from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Any

from app.core.models import WorkoutSession


def session_to_dict(session: WorkoutSession) -> dict[str, Any]:
    """
    Convert a workout session to a dictionary for JSON export.

    Args:
        session: The workout session to convert

    Returns:
        Dictionary representation of the session
    """
    return {
        "session_id": str(session.id),
        "template_id": str(session.template_id) if session.template_id else None,
        "template_name": session.template_name,
        "started_at": session.started_at.isoformat(),
        "ended_at": session.ended_at.isoformat() if session.ended_at else None,
        "duration_seconds": session.duration_seconds,
        "notes": session.notes,
        "exercises": [
            {
                "name": ex.name,
                "order_index": ex.order_index,
                "uses_weight": ex.uses_weight,
                "sets": [
                    {
                        "reps": s.reps,
                        "weight": s.weight,
                        "created_at": s.created_at.isoformat(),
                    }
                    for s in ex.sets
                ],
            }
            for ex in session.exercises
        ],
        "summary": {
            "total_exercises": len(session.exercises),
            "total_sets": session.total_sets,
            "total_reps": session.total_reps,
            "total_volume": session.total_volume,
        },
    }


def export_session_json(session: WorkoutSession, filepath: Path) -> Path:
    """
    Export a workout session to JSON file.

    Args:
        session: The workout session to export
        filepath: Path to save the JSON file

    Returns:
        Path to the saved file
    """
    data = session_to_dict(session)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return filepath


def export_session_json_string(session: WorkoutSession) -> str:
    """
    Export a workout session to JSON string.

    Args:
        session: The workout session to export

    Returns:
        JSON string representation
    """
    data = session_to_dict(session)
    return json.dumps(data, indent=2, ensure_ascii=False)


def export_session_csv(session: WorkoutSession, filepath: Path) -> Path:
    """
    Export a workout session to CSV file.

    The CSV format has one row per set with columns:
    exercise, set_number, reps, weight, created_at

    Args:
        session: The workout session to export
        filepath: Path to save the CSV file

    Returns:
        Path to the saved file
    """
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Write header
        writer.writerow(["exercise", "set_number", "reps", "weight", "created_at"])

        # Write sets
        for exercise in session.exercises:
            for set_num, s in enumerate(exercise.sets, start=1):
                writer.writerow(
                    [
                        exercise.name,
                        set_num,
                        s.reps,
                        s.weight if s.weight is not None else "",
                        s.created_at.isoformat(),
                    ]
                )

    return filepath


def export_session_csv_string(session: WorkoutSession) -> str:
    """
    Export a workout session to CSV string.

    Args:
        session: The workout session to export

    Returns:
        CSV string representation
    """
    output = StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(["exercise", "set_number", "reps", "weight", "created_at"])

    # Write sets
    for exercise in session.exercises:
        for set_num, s in enumerate(exercise.sets, start=1):
            writer.writerow(
                [
                    exercise.name,
                    set_num,
                    s.reps,
                    s.weight if s.weight is not None else "",
                    s.created_at.isoformat(),
                ]
            )

    return output.getvalue()


def generate_export_filename(
    session: WorkoutSession,
    extension: str,
) -> str:
    """
    Generate a filename for export.

    Args:
        session: The workout session
        extension: File extension (json or csv)

    Returns:
        Filename string
    """
    date_str = session.started_at.strftime("%Y-%m-%d")
    name = session.template_name or "Workout"
    # Clean the name for use in filename
    safe_name = "".join(c if c.isalnum() or c in " -_" else "" for c in name)
    safe_name = safe_name.replace(" ", "_")
    return f"ironlog_{safe_name}_{date_str}.{extension}"
