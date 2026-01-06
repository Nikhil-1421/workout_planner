"""Exercise detail view for logging sets."""

from typing import TYPE_CHECKING, Optional
from uuid import UUID

import toga
from toga.style import Pack
from toga.style.pack import BOLD, CENTER, COLUMN, ROW

from app.core.models import SessionExercise, Set, format_weight
from app.ui.components import (
    chip_button,
    flex_spacer,
    number_input,
    primary_button,
    screen_container,
    secondary_button,
    spacer,
    text_button,
)
from app.ui.theme import Theme

if TYPE_CHECKING:
    from app.main import IronLogApp


class ExerciseDetailView:
    """View for logging sets for a specific exercise."""

    def __init__(
        self,
        app: "IronLogApp",
        session_id: UUID,
        exercise_id: UUID,
    ) -> None:
        self.app = app
        self.session_id = session_id
        self.exercise_id = exercise_id
        self.exercise: Optional[SessionExercise] = None

        # Input state
        self.reps_input: Optional[toga.TextInput] = None
        self.weight_input: Optional[toga.TextInput] = None
        self.current_reps: int = 0
        self.current_weight: Optional[float] = None

        # Load exercise
        self.refresh_exercise()

        # Get last used weight for this exercise
        self.last_weight = self.app.session_repo.get_last_weight_for_exercise(
            self.exercise.name if self.exercise else ""
        )

    def refresh_exercise(self) -> None:
        """Reload exercise from database."""
        session = self.app.session_repo.get_by_id(self.session_id)
        if session:
            for ex in session.exercises:
                if ex.id == self.exercise_id:
                    self.exercise = ex
                    break

    def create_view(self) -> toga.Box:
        """Create the exercise detail view."""
        if not self.exercise:
            return screen_container([
                toga.Label(
                    text="Exercise not found",
                    style=Pack(color=Theme.TEXT_TERTIARY),
                )
            ])

        children = []

        # Header with back button
        children.append(self._create_header())

        # Exercise name
        children.append(
            toga.Label(
                text=self.exercise.name,
                style=Pack(
                    font_size=Theme.FONT_SIZE_2XL,
                    font_weight=BOLD,
                    color=Theme.TEXT_PRIMARY,
                    padding_bottom=Theme.SPACING_SM,
                ),
            )
        )

        # Weight indicator
        if not self.exercise.uses_weight:
            children.append(
                toga.Label(
                    text="Bodyweight Exercise",
                    style=Pack(
                        font_size=Theme.FONT_SIZE_SM,
                        color=Theme.TEXT_SECONDARY,
                        padding_bottom=Theme.SPACING_LG,
                    ),
                )
            )

        children.append(spacer(Theme.SPACING_LG))

        # Input section
        children.append(self._create_input_section())

        children.append(spacer(Theme.SPACING_XL))

        # Add set button
        children.append(self._create_add_set_button())

        children.append(spacer(Theme.SPACING_XL))

        # Set history (recent first)
        children.append(self._create_set_history())

        children.append(flex_spacer())

        return screen_container(children)

    def _create_header(self) -> toga.Box:
        """Create header with back navigation."""

        def on_back(widget: toga.Widget) -> None:
            self.app.navigate_to_session(self.session_id)

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
                self._create_delete_button(),
            ],
            style=Pack(
                direction=ROW,
                padding_bottom=Theme.SPACING_SM,
            ),
        )

    def _create_delete_button(self) -> toga.Button:
        """Create delete exercise button."""

        def on_delete(widget: toga.Widget) -> None:
            async def confirm_delete(dialog_app: toga.App) -> None:
                result = await dialog_app.main_window.confirm_dialog(
                    title="Delete Exercise?",
                    message="This will delete the exercise and all its sets.",
                )
                if result:
                    self.app.session_repo.delete_exercise(self.exercise_id)
                    self.app.navigate_to_session(self.session_id)

            self.app.add_background_task(confirm_delete)

        return toga.Button(
            text="Delete",
            on_press=on_delete,
            style=Pack(
                padding=Theme.SPACING_SM,
                background_color=Theme.BACKGROUND,
                color=Theme.DANGER,
                font_size=Theme.FONT_SIZE_SM,
            ),
        )

    def _create_input_section(self) -> toga.Box:
        """Create the reps and weight input section."""
        children = []

        # Reps input
        children.append(
            toga.Label(
                text="Reps",
                style=Pack(
                    font_size=Theme.FONT_SIZE_SM,
                    color=Theme.TEXT_SECONDARY,
                    padding_bottom=Theme.SPACING_XS,
                ),
            )
        )

        self.reps_input = toga.TextInput(
            placeholder="0",
            style=Pack(
                padding=Theme.SPACING_MD,
                height=Theme.BUTTON_HEIGHT_LG,
                background_color=Theme.SURFACE,
                color=Theme.TEXT_PRIMARY,
                font_size=Theme.FONT_SIZE_2XL,
            ),
        )
        children.append(self.reps_input)

        # Quick-add chips for reps
        children.append(spacer(Theme.SPACING_SM))
        children.append(self._create_reps_chips())

        children.append(spacer(Theme.SPACING_LG))

        # Weight input (if applicable)
        if self.exercise and self.exercise.uses_weight:
            children.append(
                toga.Label(
                    text="Weight (lbs)",
                    style=Pack(
                        font_size=Theme.FONT_SIZE_SM,
                        color=Theme.TEXT_SECONDARY,
                        padding_bottom=Theme.SPACING_XS,
                    ),
                )
            )

            # Pre-fill with last weight if available
            default_weight = ""
            if self.last_weight:
                default_weight = str(int(self.last_weight))

            self.weight_input = toga.TextInput(
                value=default_weight,
                placeholder="0",
                style=Pack(
                    padding=Theme.SPACING_MD,
                    height=Theme.BUTTON_HEIGHT_LG,
                    background_color=Theme.SURFACE,
                    color=Theme.TEXT_PRIMARY,
                    font_size=Theme.FONT_SIZE_2XL,
                ),
            )
            children.append(self.weight_input)

            # Quick-add chips for weight
            children.append(spacer(Theme.SPACING_SM))
            children.append(self._create_weight_chips())

        return toga.Box(
            children=children,
            style=Pack(direction=COLUMN),
        )

    def _create_reps_chips(self) -> toga.Box:
        """Create quick-add chips for common rep values."""
        chips = []

        for reps in Theme.QUICK_REPS:

            def on_chip(widget: toga.Widget, r: int = reps) -> None:
                if self.reps_input:
                    self.reps_input.value = str(r)

            chips.append(
                toga.Button(
                    text=str(reps),
                    on_press=on_chip,
                    style=Pack(
                        padding_left=Theme.SPACING_MD,
                        padding_right=Theme.SPACING_MD,
                        padding_top=Theme.SPACING_SM,
                        padding_bottom=Theme.SPACING_SM,
                        background_color=Theme.SURFACE,
                        color=Theme.TEXT_SECONDARY,
                        font_size=Theme.FONT_SIZE_SM,
                    ),
                )
            )
            chips.append(toga.Box(style=Pack(width=Theme.SPACING_SM)))

        # Copy last set button
        if self.exercise and self.exercise.sets:

            def on_copy_last(widget: toga.Widget) -> None:
                if self.exercise and self.exercise.sets and self.reps_input:
                    last_set = self.exercise.sets[-1]
                    self.reps_input.value = str(last_set.reps)
                    if self.weight_input and last_set.weight:
                        self.weight_input.value = str(int(last_set.weight))

            chips.append(
                toga.Button(
                    text="Copy Last",
                    on_press=on_copy_last,
                    style=Pack(
                        padding_left=Theme.SPACING_MD,
                        padding_right=Theme.SPACING_MD,
                        padding_top=Theme.SPACING_SM,
                        padding_bottom=Theme.SPACING_SM,
                        background_color=Theme.PRIMARY_MUTED,
                        color=Theme.PRIMARY,
                        font_size=Theme.FONT_SIZE_SM,
                    ),
                )
            )

        return toga.Box(
            children=chips,
            style=Pack(direction=ROW),
        )

    def _create_weight_chips(self) -> toga.Box:
        """Create quick-add chips for weight adjustments."""
        if not self.exercise or not self.exercise.uses_weight:
            return toga.Box()

        chips = []

        # Get current weight value
        def get_current_weight() -> float:
            if self.weight_input and self.weight_input.value:
                try:
                    return float(self.weight_input.value)
                except ValueError:
                    pass
            return self.last_weight or 0

        # +5 button
        def on_plus_5(widget: toga.Widget) -> None:
            if self.weight_input:
                current = get_current_weight()
                self.weight_input.value = str(int(current + 5))

        chips.append(
            toga.Button(
                text="+5",
                on_press=on_plus_5,
                style=Pack(
                    padding_left=Theme.SPACING_MD,
                    padding_right=Theme.SPACING_MD,
                    padding_top=Theme.SPACING_SM,
                    padding_bottom=Theme.SPACING_SM,
                    background_color=Theme.SURFACE,
                    color=Theme.TEXT_SECONDARY,
                    font_size=Theme.FONT_SIZE_SM,
                ),
            )
        )
        chips.append(toga.Box(style=Pack(width=Theme.SPACING_SM)))

        # +10 button
        def on_plus_10(widget: toga.Widget) -> None:
            if self.weight_input:
                current = get_current_weight()
                self.weight_input.value = str(int(current + 10))

        chips.append(
            toga.Button(
                text="+10",
                on_press=on_plus_10,
                style=Pack(
                    padding_left=Theme.SPACING_MD,
                    padding_right=Theme.SPACING_MD,
                    padding_top=Theme.SPACING_SM,
                    padding_bottom=Theme.SPACING_SM,
                    background_color=Theme.SURFACE,
                    color=Theme.TEXT_SECONDARY,
                    font_size=Theme.FONT_SIZE_SM,
                ),
            )
        )
        chips.append(toga.Box(style=Pack(width=Theme.SPACING_SM)))

        # -5 button
        def on_minus_5(widget: toga.Widget) -> None:
            if self.weight_input:
                current = get_current_weight()
                new_val = max(0, current - 5)
                self.weight_input.value = str(int(new_val))

        chips.append(
            toga.Button(
                text="-5",
                on_press=on_minus_5,
                style=Pack(
                    padding_left=Theme.SPACING_MD,
                    padding_right=Theme.SPACING_MD,
                    padding_top=Theme.SPACING_SM,
                    padding_bottom=Theme.SPACING_SM,
                    background_color=Theme.SURFACE,
                    color=Theme.TEXT_SECONDARY,
                    font_size=Theme.FONT_SIZE_SM,
                ),
            )
        )

        return toga.Box(
            children=chips,
            style=Pack(direction=ROW),
        )

    def _create_add_set_button(self) -> toga.Box:
        """Create the add set button."""

        def on_add_set(widget: toga.Widget) -> None:
            self._add_set()

        return toga.Box(
            children=[
                primary_button("Log Set", on_press=on_add_set),
            ],
            style=Pack(direction=ROW),
        )

    def _add_set(self) -> None:
        """Add a new set with current input values."""
        if not self.exercise or not self.reps_input:
            return

        # Parse reps
        try:
            reps = int(self.reps_input.value)
            if reps <= 0:
                return
        except ValueError:
            return

        # Parse weight (if applicable)
        weight: Optional[float] = None
        if self.exercise.uses_weight and self.weight_input:
            try:
                weight = float(self.weight_input.value)
            except ValueError:
                pass  # Weight is optional

        # Create and save set
        new_set = Set.create(
            session_exercise_id=self.exercise_id,
            reps=reps,
            weight=weight,
        )
        self.app.session_repo.save_set(new_set)

        # Add to local list
        self.exercise.sets.append(new_set)

        # Clear reps input, keep weight
        self.reps_input.value = ""

        # Refresh view
        self.app.navigate_to_exercise(self.session_id, self.exercise_id)

    def _create_set_history(self) -> toga.Box:
        """Create the set history list (most recent first)."""
        if not self.exercise or not self.exercise.sets:
            return toga.Box(
                children=[
                    toga.Label(
                        text="No sets logged yet",
                        style=Pack(
                            font_size=Theme.FONT_SIZE_SM,
                            color=Theme.TEXT_TERTIARY,
                            text_align=CENTER,
                        ),
                    ),
                ],
                style=Pack(direction=COLUMN, alignment=CENTER),
            )

        children = [
            toga.Label(
                text="Sets",
                style=Pack(
                    font_size=Theme.FONT_SIZE_SM,
                    color=Theme.TEXT_SECONDARY,
                    padding_bottom=Theme.SPACING_SM,
                ),
            ),
        ]

        # Show sets in reverse order (newest first)
        for i, workout_set in enumerate(reversed(self.exercise.sets)):
            set_num = len(self.exercise.sets) - i
            children.append(self._create_set_item(set_num, workout_set))

        return toga.Box(
            children=children,
            style=Pack(direction=COLUMN),
        )

    def _create_set_item(self, set_num: int, workout_set: Set) -> toga.Box:
        """Create a single set history item."""
        # Format set info
        if self.exercise and self.exercise.uses_weight and workout_set.weight:
            set_text = f"{int(workout_set.weight)} × {workout_set.reps}"
        else:
            set_text = f"{workout_set.reps} reps"

        def on_delete(widget: toga.Widget) -> None:
            async def confirm_delete(dialog_app: toga.App) -> None:
                result = await dialog_app.main_window.confirm_dialog(
                    title="Delete Set?",
                    message=f"Delete set {set_num}?",
                )
                if result:
                    self.app.session_repo.delete_set(workout_set.id)
                    self.app.navigate_to_exercise(self.session_id, self.exercise_id)

            self.app.add_background_task(confirm_delete)

        return toga.Box(
            children=[
                toga.Label(
                    text=f"Set {set_num}",
                    style=Pack(
                        font_size=Theme.FONT_SIZE_SM,
                        color=Theme.TEXT_SECONDARY,
                        width=60,
                    ),
                ),
                toga.Label(
                    text=set_text,
                    style=Pack(
                        font_size=Theme.FONT_SIZE_BASE,
                        color=Theme.TEXT_PRIMARY,
                        flex=1,
                    ),
                ),
                toga.Button(
                    text="×",
                    on_press=on_delete,
                    style=Pack(
                        padding=Theme.SPACING_XS,
                        background_color=Theme.SURFACE,
                        color=Theme.TEXT_TERTIARY,
                        font_size=Theme.FONT_SIZE_BASE,
                        width=30,
                    ),
                ),
            ],
            style=Pack(
                direction=ROW,
                padding=Theme.SPACING_SM,
                background_color=Theme.SURFACE,
                alignment=CENTER,
            ),
        )


def create_exercise_detail_view(
    app: "IronLogApp",
    session_id: UUID,
    exercise_id: UUID,
) -> toga.Box:
    """Create an exercise detail view."""
    view = ExerciseDetailView(app, session_id, exercise_id)
    return view.create_view()
