"""Active workout session view."""

from typing import TYPE_CHECKING, Optional
from uuid import UUID

import toga
from toga.style import Pack
from toga.style.pack import BOLD, CENTER, COLUMN, ROW

from app.core.models import SessionExercise, WorkoutSession, format_duration
from app.core.timer import Timer
from app.ui.components import (
    body_text,
    danger_button,
    flex_spacer,
    primary_button,
    screen_container,
    secondary_button,
    secondary_text,
    spacer,
    text_button,
    title_text,
)
from app.ui.theme import Theme

if TYPE_CHECKING:
    from app.main import IronLogApp


class SessionView:
    """Active workout session view with timer."""

    def __init__(self, app: "IronLogApp", session_id: UUID) -> None:
        self.app = app
        self.session_id = session_id
        self.session: Optional[WorkoutSession] = None
        self.timer: Optional[Timer] = None
        self.timer_label: Optional[toga.Label] = None
        self.timer_handle: Optional[object] = None

        # Load session
        self.refresh_session()

        # Initialize timer
        self._setup_timer()

    def refresh_session(self) -> None:
        """Reload session from database."""
        self.session = self.app.session_repo.get_by_id(self.session_id)

    def _setup_timer(self) -> None:
        """Set up the workout timer."""
        self.timer = Timer(
            on_tick=self._on_timer_tick,
            on_state_change=self._on_timer_state_change,
        )

        # Restore timer state if exists
        saved_state = self.app.state_repo.get_timer_state()
        if saved_state and saved_state.is_running:
            self.timer.restore(saved_state)
        else:
            # Start fresh timer
            self.timer.start()

    def _on_timer_tick(self, time_str: str) -> None:
        """Handle timer tick."""
        if self.timer_label:
            self.timer_label.text = time_str

    def _on_timer_state_change(self, state) -> None:  # noqa: ANN001
        """Handle timer state change."""
        self.app.state_repo.set_timer_state(state)

    def _start_timer_updates(self) -> None:
        """Start periodic timer updates."""
        if self.timer_handle is None:

            def update_timer() -> None:
                if self.timer and self.timer_label:
                    self.timer_label.text = self.timer.formatted_time

            # Schedule periodic updates
            self.timer_handle = self.app.loop.call_later(1.0, self._timer_tick)

    def _timer_tick(self) -> None:
        """Timer tick callback."""
        if self.timer and self.timer_label and self.timer.is_running:
            self.timer_label.text = self.timer.formatted_time
            # Schedule next tick
            self.timer_handle = self.app.loop.call_later(1.0, self._timer_tick)

    def _stop_timer_updates(self) -> None:
        """Stop periodic timer updates."""
        # Timer handle cleanup is automatic when view is destroyed
        pass

    def create_view(self) -> toga.Box:
        """Create the session view."""
        if not self.session:
            return screen_container([body_text("Session not found")])

        children = []

        # Header with back button
        children.append(self._create_header())

        # Timer section
        children.append(self._create_timer_section())
        children.append(spacer(Theme.SPACING_LG))

        # Session info
        if self.session.template_name:
            children.append(
                toga.Label(
                    text=self.session.template_name,
                    style=Pack(
                        font_size=Theme.FONT_SIZE_LG,
                        color=Theme.TEXT_PRIMARY,
                        font_weight=BOLD,
                        padding_bottom=Theme.SPACING_SM,
                    ),
                )
            )

        # Exercise list
        children.append(self._create_exercise_list())

        # Add exercise button
        children.append(spacer(Theme.SPACING_LG))
        children.append(self._create_add_exercise_button())

        children.append(flex_spacer())

        # End workout button
        children.append(spacer(Theme.SPACING_LG))
        children.append(self._create_end_workout_button())

        container = screen_container(children)

        # Start timer updates
        self._start_timer_updates()

        return container

    def _create_header(self) -> toga.Box:
        """Create header with navigation."""

        def on_back(widget: toga.Widget) -> None:
            self._stop_timer_updates()
            self.app.navigate_home()

        return toga.Box(
            children=[
                toga.Button(
                    text="← Back",
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
                padding_bottom=Theme.SPACING_SM,
            ),
        )

    def _create_timer_section(self) -> toga.Box:
        """Create the timer display and controls."""
        # Timer display
        timer_color = Theme.TIMER if self.timer and not self.timer.is_paused else Theme.TIMER_PAUSED
        self.timer_label = toga.Label(
            text=self.timer.formatted_time if self.timer else "0:00",
            style=Pack(
                font_size=Theme.FONT_SIZE_TIMER,
                font_weight=BOLD,
                color=timer_color,
                text_align=CENTER,
                padding_bottom=Theme.SPACING_SM,
            ),
        )

        # Timer controls
        def on_pause_resume(widget: toga.Widget) -> None:
            if self.timer:
                if self.timer.is_paused:
                    self.timer.resume()
                    widget.text = "Pause"
                    if self.timer_label:
                        self.timer_label.style.color = Theme.TIMER
                    self._start_timer_updates()
                else:
                    self.timer.pause()
                    widget.text = "Resume"
                    if self.timer_label:
                        self.timer_label.style.color = Theme.TIMER_PAUSED

        pause_text = "Resume" if self.timer and self.timer.is_paused else "Pause"
        pause_btn = toga.Button(
            text=pause_text,
            on_press=on_pause_resume,
            style=Pack(
                padding=Theme.SPACING_SM,
                background_color=Theme.SURFACE,
                color=Theme.TEXT_PRIMARY,
                font_size=Theme.FONT_SIZE_SM,
            ),
        )

        return toga.Box(
            children=[
                self.timer_label,
                toga.Box(
                    children=[pause_btn],
                    style=Pack(direction=ROW, alignment=CENTER),
                ),
            ],
            style=Pack(
                direction=COLUMN,
                alignment=CENTER,
                padding=Theme.SPACING_BASE,
                background_color=Theme.SURFACE,
            ),
        )

    def _create_exercise_list(self) -> toga.Box:
        """Create scrollable exercise list."""
        if not self.session or not self.session.exercises:
            return toga.Box(
                children=[
                    spacer(Theme.SPACING_2XL),
                    toga.Label(
                        text="No exercises yet",
                        style=Pack(
                            font_size=Theme.FONT_SIZE_BASE,
                            color=Theme.TEXT_TERTIARY,
                            text_align=CENTER,
                        ),
                    ),
                    toga.Label(
                        text="Add an exercise to start logging",
                        style=Pack(
                            font_size=Theme.FONT_SIZE_SM,
                            color=Theme.TEXT_TERTIARY,
                            text_align=CENTER,
                            padding_top=Theme.SPACING_XS,
                        ),
                    ),
                ],
                style=Pack(direction=COLUMN, alignment=CENTER),
            )

        exercise_items = []
        for exercise in self.session.exercises:
            exercise_items.append(self._create_exercise_item(exercise))
            exercise_items.append(spacer(Theme.SPACING_SM))

        return toga.Box(
            children=exercise_items,
            style=Pack(direction=COLUMN),
        )

    def _create_exercise_item(self, exercise: SessionExercise) -> toga.Box:
        """Create an exercise list item."""

        def on_press(widget: toga.Widget) -> None:
            self.app.navigate_to_exercise(self.session_id, exercise.id)

        set_count = len(exercise.sets)
        set_text = f"{set_count} set{'s' if set_count != 1 else ''}"

        # Show last set info
        last_set_info = ""
        if exercise.sets:
            last_set = exercise.sets[-1]
            if exercise.uses_weight and last_set.weight:
                last_set_info = f"  ·  Last: {int(last_set.weight)}×{last_set.reps}"
            else:
                last_set_info = f"  ·  Last: {last_set.reps} reps"

        return toga.Box(
            children=[
                toga.Button(
                    text=f"{exercise.name}\n{set_text}{last_set_info}",
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

    def _create_add_exercise_button(self) -> toga.Box:
        """Create add exercise button."""

        def on_add_exercise(widget: toga.Widget) -> None:
            self._show_add_exercise_dialog()

        return toga.Box(
            children=[
                secondary_button("+ Add Exercise", on_press=on_add_exercise),
            ],
            style=Pack(direction=ROW),
        )

    def _show_add_exercise_dialog(self) -> None:
        """Show dialog to add a new exercise."""

        async def add_exercise_dialog(dialog_app: toga.App) -> None:
            # Simple text input for exercise name
            result = await dialog_app.main_window.dialog(
                toga.TextInputDialog(
                    title="Add Exercise",
                    message="Enter exercise name:",
                )
            )
            if result and result.strip():
                self._add_exercise(result.strip())

        self.app.add_background_task(add_exercise_dialog)

    def _add_exercise(self, name: str, uses_weight: bool = True) -> None:
        """Add a new exercise to the session."""
        if not self.session:
            return

        order_index = len(self.session.exercises)
        exercise = SessionExercise.create(
            session_id=self.session_id,
            name=name,
            order_index=order_index,
            uses_weight=uses_weight,
        )

        self.app.session_repo.save_exercise(exercise)
        self.session.exercises.append(exercise)

        # Navigate to exercise detail to log sets
        self.app.navigate_to_exercise(self.session_id, exercise.id)

    def _create_end_workout_button(self) -> toga.Box:
        """Create end workout button."""

        def on_end_workout(widget: toga.Widget) -> None:
            self._show_end_workout_confirmation()

        return toga.Box(
            children=[
                danger_button("End Workout", on_press=on_end_workout),
            ],
            style=Pack(direction=ROW),
        )

    def _show_end_workout_confirmation(self) -> None:
        """Show confirmation before ending workout."""

        async def confirm_end(dialog_app: toga.App) -> None:
            result = await dialog_app.main_window.confirm_dialog(
                title="End Workout?",
                message="This will finish your workout and save it to history.",
            )
            if result:
                self._end_workout()

        self.app.add_background_task(confirm_end)

    def _end_workout(self) -> None:
        """End the workout and save."""
        if not self.timer or not self.session:
            return

        # Stop timer and get duration
        duration = self.timer.stop()

        # Update session
        self.app.session_repo.end_session(self.session_id, duration)

        # Clear app state
        self.app.state_repo.set_active_session_id(None)
        self.app.state_repo.set_timer_state(None)

        # Stop updates
        self._stop_timer_updates()

        # Navigate to history or show summary
        self.app.navigate_home()
        self.app.tab_bar.select_tab(2)  # History tab


def create_session_view(app: "IronLogApp", session_id: UUID) -> toga.Box:
    """Create a session view."""
    view = SessionView(app, session_id)
    return view.create_view()
