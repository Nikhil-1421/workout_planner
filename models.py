"""Domain models for IronLog."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class Set:
    """A single set within an exercise."""

    id: UUID
    session_exercise_id: UUID
    reps: int
    weight: Optional[float]  # None for bodyweight exercises
    created_at: datetime

    @classmethod
    def create(
        cls,
        session_exercise_id: UUID,
        reps: int,
        weight: Optional[float] = None,
    ) -> "Set":
        """Create a new set with auto-generated ID and timestamp."""
        return cls(
            id=uuid4(),
            session_exercise_id=session_exercise_id,
            reps=reps,
            weight=weight,
            created_at=datetime.now(),
        )


@dataclass
class SessionExercise:
    """An exercise within a workout session."""

    id: UUID
    session_id: UUID
    name: str
    order_index: int
    uses_weight: bool
    sets: list[Set] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        session_id: UUID,
        name: str,
        order_index: int,
        uses_weight: bool = True,
    ) -> "SessionExercise":
        """Create a new session exercise with auto-generated ID."""
        return cls(
            id=uuid4(),
            session_id=session_id,
            name=name,
            order_index=order_index,
            uses_weight=uses_weight,
            sets=[],
        )

    @classmethod
    def from_template_exercise(
        cls,
        session_id: UUID,
        template_exercise: "TemplateExercise",
    ) -> "SessionExercise":
        """Create a session exercise from a template exercise."""
        return cls(
            id=uuid4(),
            session_id=session_id,
            name=template_exercise.name,
            order_index=template_exercise.order_index,
            uses_weight=template_exercise.uses_weight,
            sets=[],
        )


@dataclass
class WorkoutSession:
    """A workout session (active or completed)."""

    id: UUID
    template_id: Optional[UUID]
    template_name: Optional[str]  # Denormalized for history display
    started_at: datetime
    ended_at: Optional[datetime]
    duration_seconds: Optional[int]
    notes: Optional[str]
    exercises: list[SessionExercise] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        template_id: Optional[UUID] = None,
        template_name: Optional[str] = None,
    ) -> "WorkoutSession":
        """Create a new workout session with auto-generated ID and timestamp."""
        return cls(
            id=uuid4(),
            template_id=template_id,
            template_name=template_name,
            started_at=datetime.now(),
            ended_at=None,
            duration_seconds=None,
            notes=None,
            exercises=[],
        )

    @property
    def is_active(self) -> bool:
        """Check if this session is still active (not ended)."""
        return self.ended_at is None

    @property
    def total_sets(self) -> int:
        """Get total number of sets in this session."""
        return sum(len(ex.sets) for ex in self.exercises)

    @property
    def total_reps(self) -> int:
        """Get total number of reps in this session."""
        return sum(s.reps for ex in self.exercises for s in ex.sets)

    @property
    def total_volume(self) -> float:
        """Get total volume (weight * reps) in this session."""
        total = 0.0
        for ex in self.exercises:
            for s in ex.sets:
                if s.weight is not None:
                    total += s.weight * s.reps
        return total

    def formatted_duration(self) -> str:
        """Get formatted duration string."""
        if self.duration_seconds is None:
            return "--:--"
        return format_duration(self.duration_seconds)


@dataclass
class TemplateExercise:
    """An exercise within a workout template."""

    id: UUID
    template_id: UUID
    name: str
    order_index: int
    uses_weight: bool

    @classmethod
    def create(
        cls,
        template_id: UUID,
        name: str,
        order_index: int,
        uses_weight: bool = True,
    ) -> "TemplateExercise":
        """Create a new template exercise with auto-generated ID."""
        return cls(
            id=uuid4(),
            template_id=template_id,
            name=name,
            order_index=order_index,
            uses_weight=uses_weight,
        )


@dataclass
class WorkoutTemplate:
    """A reusable workout template."""

    id: UUID
    name: str
    created_at: datetime
    exercises: list[TemplateExercise] = field(default_factory=list)

    @classmethod
    def create(cls, name: str) -> "WorkoutTemplate":
        """Create a new template with auto-generated ID and timestamp."""
        return cls(
            id=uuid4(),
            name=name,
            created_at=datetime.now(),
            exercises=[],
        )

    @property
    def exercise_count(self) -> int:
        """Get number of exercises in this template."""
        return len(self.exercises)


@dataclass
class TimerState:
    """Persistent timer state."""

    is_running: bool
    is_paused: bool
    start_time: Optional[datetime]
    pause_time: Optional[datetime]
    accumulated_seconds: float  # Time accumulated before pause

    @classmethod
    def initial(cls) -> "TimerState":
        """Create initial timer state (stopped)."""
        return cls(
            is_running=False,
            is_paused=False,
            start_time=None,
            pause_time=None,
            accumulated_seconds=0.0,
        )


@dataclass
class AppState:
    """Application state that persists across launches."""

    active_session_id: Optional[UUID]
    last_template_id: Optional[UUID]
    timer_state: Optional[TimerState]


def format_duration(seconds: int) -> str:
    """Format duration in seconds to mm:ss or hh:mm:ss."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        return f"{hours:d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:d}:{secs:02d}"


def format_weight(weight: Optional[float]) -> str:
    """Format weight for display."""
    if weight is None:
        return "BW"  # Bodyweight
    if weight == int(weight):
        return str(int(weight))
    return f"{weight:.1f}"


def format_datetime(dt: datetime) -> str:
    """Format datetime for display."""
    return dt.strftime("%b %d, %Y at %I:%M %p")


def format_date(dt: datetime) -> str:
    """Format date for display."""
    today = datetime.now().date()
    date = dt.date()

    if date == today:
        return "Today"
    days_diff = (today - date).days
    if days_diff == 1:
        return "Yesterday"
    if days_diff < 7:
        return dt.strftime("%A")  # Day name
    return dt.strftime("%b %d, %Y")
