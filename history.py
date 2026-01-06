"""History tab - View past workout sessions."""

from typing import TYPE_CHECKING, Optional
from uuid import UUID

import toga
from toga.style import Pack
from toga.style.pack import BOLD, CENTER, COLUMN, ROW

from app.core.models import WorkoutSession, format_date, format_datetime, format_weight
from app.ui.components import (
    empty_state,
    flex_spacer,
    screen_container,
    secondary_text,
    spacer,
    title_text,
)
from app.ui.theme import Theme

if TYPE_CHECKING:
    from app.main import IronLogApp


def create_history_tab(app: "IronLogApp") -> toga.Box:
    """Create the History tab content."""
    sessions = app.session_repo.get_all(limit=50)

    # Filter to only completed sessions
    completed_sessions = [s for s in sessions if s.ended_at is not None]

    children = [
        # Header
        toga.Box(
            children=[
                title_text("History"),
            ],
            style=Pack(direction=ROW, padding_bottom=Theme.SPACING_LG),
        ),
    ]

    if completed_sessions:
        # Group sessions by date
        current_date = None
        for session in completed_sessions:
            session_date = format_date(session.started_at)

            if session_date != current_date:
                current_date = session_date
                children.append(
                    toga.Label(
                        text=session_date,
                        style=Pack(
                            font_size=Theme.FONT_SIZE_SM,
                            color=Theme.TEXT_TERTIARY,
                            padding_top=Theme.SPACING_LG if len(children) > 1 else 0,
                            padding_bottom=Theme.SPACING_SM,
                        ),
                    )
                )

            children.append(_create_session_card(app, session))
            children.append(spacer(Theme.SPACING_SM))
    else:
        children.append(
            empty_state(
                Theme.EMPTY_HISTORY,
                Theme.EMPTY_HISTORY_HINT,
            )
        )

    children.append(flex_spacer())

    return screen_container(children)


def _create_session_card(app: "IronLogApp", session: WorkoutSession) -> toga.Box:
    """Create a session history card."""

    def on_press(widget: toga.Widget) -> None:
        app.navigate_to_session_detail(session.id)

    name = session.template_name or "Custom Workout"
    duration = session.formatted_duration()

    # Summary stats
    exercise_count = len(session.exercises)
    set_count = session.total_sets

    return toga.Box(
        children=[
            toga.Button(
                text=f"{name}\n{duration} · {exercise_count} exercises · {set_count} sets",
                on_press=on_press,
                style=Pack(
                    padding=Theme.SPACING_BASE,
                    background_color=Theme.SURFACE,
                    color=Theme.TEXT_PRIMARY,
                    font_size=Theme.FONT_SIZE_BASE,
                    flex=1,
                    text_align=CENTER,
                ),
            ),
        ],
        style=Pack(direction=ROW),
    )


class SessionDetailView:
    """Read-only view of a completed session."""

    def __init__(self, app: "IronLogApp", session_id: UUID) -> None:
        self.app = app
        self.session_id = session_id
        self.session: Optional[WorkoutSession] = None

        # Load session
        self.refresh_session()

    def refresh_session(self) -> None:
        """Reload session from database."""
        self.session = self.app.session_repo.get_by_id(self.session_id)

    def create_view(self) -> toga.Box:
        """Create the session detail view."""
        if not self.session:
            return screen_container([
                toga.Label(
                    text="Session not found",
                    style=Pack(color=Theme.TEXT_TERTIARY),
                )
            ])

        children = []

        # Header
        children.append(self._create_header())

        # Session info
        name = self.session.template_name or "Custom Workout"
        children.append(
            toga.Label(
                text=name,
                style=Pack(
                    font_size=Theme.FONT_SIZE_2XL,
                    font_weight=BOLD,
                    color=Theme.TEXT_PRIMARY,
                    padding_bottom=Theme.SPACING_XS,
                ),
            )
        )

        # Date and duration
        date_str = format_datetime(self.session.started_at)
        duration = self.session.formatted_duration()
        children.append(
            toga.Label(
                text=f"{date_str}  ·  {duration}",
                style=Pack(
                    font_size=Theme.FONT_SIZE_SM,
                    color=Theme.TEXT_SECONDARY,
                    padding_bottom=Theme.SPACING_LG,
                ),
            )
        )

        # Summary stats
        children.append(self._create_summary())
        children.append(spacer(Theme.SPACING_XL))

        # Exercise list
        children.append(
            toga.Label(
                text="Exercises",
                style=Pack(
                    font_size=Theme.FONT_SIZE_SM,
                    color=Theme.TEXT_SECONDARY,
                    padding_bottom=Theme.SPACING_SM,
                ),
            )
        )

        for exercise in self.session.exercises:
            children.append(self._create_exercise_section(exercise))
            children.append(spacer(Theme.SPACING_MD))

        children.append(flex_spacer())

        return screen_container(children)

    def _create_header(self) -> toga.Box:
        """Create header with back button."""

        def on_back(widget: toga.Widget) -> None:
            self.app.navigate_to_history()

        return toga.Box(
            children=[
                toga.Button(
                    text="← History",
                    on_press=on_back,
                    style=Pack(
                        padding=Theme.SPACING_SM,
                        background_color=Theme.BACKGROUND,
                        color=Theme.PRIMARY,
                        font_size=Theme.FONT_SIZE_BASE,
                    ),
                ),
                flex_spacer(),
            ],
            style=Pack(
                direction=ROW,
                padding_bottom=Theme.SPACING_LG,
            ),
        )

    def _create_summary(self) -> toga.Box:
        """Create session summary stats."""
        if not self.session:
            return toga.Box()

        return toga.Box(
            children=[
                self._stat_item(str(len(self.session.exercises)), "Exercises"),
                self._stat_item(str(self.session.total_sets), "Sets"),
                self._stat_item(str(self.session.total_reps), "Reps"),
                self._stat_item(f"{int(self.session.total_volume)}", "Volume"),
            ],
            style=Pack(
                direction=ROW,
                padding=Theme.SPACING_BASE,
                background_color=Theme.SURFACE,
            ),
        )

    def _stat_item(self, value: str, label: str) -> toga.Box:
        """Create a stat item."""
        return toga.Box(
            children=[
                toga.Label(
                    text=value,
                    style=Pack(
                        font_size=Theme.FONT_SIZE_XL,
                        font_weight=BOLD,
                        color=Theme.TEXT_PRIMARY,
                        text_align=CENTER,
                    ),
                ),
                toga.Label(
                    text=label,
                    style=Pack(
                        font_size=Theme.FONT_SIZE_XS,
                        color=Theme.TEXT_SECONDARY,
                        text_align=CENTER,
                    ),
                ),
            ],
            style=Pack(
                direction=COLUMN,
                flex=1,
                alignment=CENTER,
            ),
        )

    def _create_exercise_section(self, exercise) -> toga.Box:  # noqa: ANN001
        """Create an exercise section with its sets."""
        children = [
            toga.Label(
                text=exercise.name,
                style=Pack(
                    font_size=Theme.FONT_SIZE_BASE,
                    font_weight=BOLD,
                    color=Theme.TEXT_PRIMARY,
                    padding_bottom=Theme.SPACING_SM,
                ),
            ),
        ]

        # List sets
        for i, workout_set in enumerate(exercise.sets):
            set_num = i + 1
            if exercise.uses_weight and workout_set.weight:
                set_text = f"Set {set_num}: {int(workout_set.weight)} × {workout_set.reps}"
            else:
                set_text = f"Set {set_num}: {workout_set.reps} reps"

            children.append(
                toga.Label(
                    text=set_text,
                    style=Pack(
                        font_size=Theme.FONT_SIZE_SM,
                        color=Theme.TEXT_SECONDARY,
                        padding_left=Theme.SPACING_SM,
                        padding_bottom=Theme.SPACING_XS,
                    ),
                )
            )

        return toga.Box(
            children=children,
            style=Pack(
                direction=COLUMN,
                padding=Theme.SPACING_BASE,
                background_color=Theme.SURFACE,
            ),
        )


def create_session_detail_view(app: "IronLogApp", session_id: UUID) -> toga.Box:
    """Create a session detail view."""
    view = SessionDetailView(app, session_id)
    return view.create_view()
