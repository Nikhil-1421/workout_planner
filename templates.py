"""Templates tab - Manage workout templates."""

from typing import TYPE_CHECKING, Optional
from uuid import UUID

import toga
from toga.style import Pack
from toga.style.pack import BOLD, CENTER, COLUMN, ROW

from app.core.models import SessionExercise, TemplateExercise, WorkoutSession, WorkoutTemplate
from app.ui.components import (
    danger_button,
    empty_state,
    flex_spacer,
    primary_button,
    screen_container,
    secondary_button,
    spacer,
    text_input,
    title_text,
)
from app.ui.theme import Theme

if TYPE_CHECKING:
    from app.main import IronLogApp


def create_templates_tab(app: "IronLogApp") -> toga.Box:
    """Create the Templates tab content."""
    templates = app.template_repo.get_all()

    children = [
        # Header
        toga.Box(
            children=[
                title_text("Templates"),
                flex_spacer(),
            ],
            style=Pack(direction=ROW, padding_bottom=Theme.SPACING_LG),
        ),
        # Add template button
        _create_add_template_button(app),
        spacer(Theme.SPACING_LG),
    ]

    if templates:
        # Template list
        for template in templates:
            children.append(_create_template_card(app, template))
            children.append(spacer(Theme.SPACING_SM))
    else:
        children.append(
            empty_state(
                Theme.EMPTY_TEMPLATES,
                Theme.EMPTY_TEMPLATES_HINT,
            )
        )

    children.append(flex_spacer())

    return screen_container(children)


def _create_add_template_button(app: "IronLogApp") -> toga.Box:
    """Create the add template button."""

    def on_add_template(widget: toga.Widget) -> None:
        _show_add_template_dialog(app)

    return toga.Box(
        children=[
            primary_button("+ New Template", on_press=on_add_template),
        ],
        style=Pack(direction=ROW),
    )


def _show_add_template_dialog(app: "IronLogApp") -> None:
    """Show dialog to create a new template."""

    async def add_template_dialog(dialog_app: toga.App) -> None:
        result = await dialog_app.main_window.dialog(
            toga.TextInputDialog(
                title="New Template",
                message="Enter template name:",
            )
        )
        if result and result.strip():
            template = WorkoutTemplate.create(result.strip())
            app.template_repo.save(template)
            # Navigate to template edit
            app.navigate_to_template_edit(template.id)

    app.add_background_task(add_template_dialog)


def _create_template_card(app: "IronLogApp", template: WorkoutTemplate) -> toga.Box:
    """Create a template card."""

    def on_press(widget: toga.Widget) -> None:
        app.navigate_to_template_edit(template.id)

    exercise_count = len(template.exercises)
    exercise_text = f"{exercise_count} exercise{'s' if exercise_count != 1 else ''}"

    if template.exercises:
        exercise_names = ", ".join(ex.name for ex in template.exercises[:3])
        if len(template.exercises) > 3:
            exercise_names += "..."
    else:
        exercise_names = "No exercises yet"

    return toga.Box(
        children=[
            toga.Button(
                text=f"{template.name}\n{exercise_text} · {exercise_names}",
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


class TemplateEditView:
    """View for editing a workout template."""

    def __init__(self, app: "IronLogApp", template_id: UUID) -> None:
        self.app = app
        self.template_id = template_id
        self.template: Optional[WorkoutTemplate] = None
        self.name_input: Optional[toga.TextInput] = None

        # Load template
        self.refresh_template()

    def refresh_template(self) -> None:
        """Reload template from database."""
        self.template = self.app.template_repo.get_by_id(self.template_id)

    def create_view(self) -> toga.Box:
        """Create the template edit view."""
        if not self.template:
            return screen_container([
                toga.Label(
                    text="Template not found",
                    style=Pack(color=Theme.TEXT_TERTIARY),
                )
            ])

        children = []

        # Header
        children.append(self._create_header())

        # Template name input
        children.append(
            toga.Label(
                text="Template Name",
                style=Pack(
                    font_size=Theme.FONT_SIZE_SM,
                    color=Theme.TEXT_SECONDARY,
                    padding_bottom=Theme.SPACING_XS,
                ),
            )
        )
        self.name_input = toga.TextInput(
            value=self.template.name,
            placeholder="Enter name",
            style=Pack(
                padding=Theme.SPACING_MD,
                height=Theme.BUTTON_HEIGHT_MD,
                background_color=Theme.SURFACE,
                color=Theme.TEXT_PRIMARY,
                font_size=Theme.FONT_SIZE_BASE,
            ),
        )
        children.append(self.name_input)

        children.append(spacer(Theme.SPACING_XL))

        # Exercises section
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

        children.append(self._create_add_exercise_button())
        children.append(spacer(Theme.SPACING_SM))

        # Exercise list
        if self.template.exercises:
            for exercise in self.template.exercises:
                children.append(self._create_exercise_item(exercise))
                children.append(spacer(Theme.SPACING_XS))
        else:
            children.append(
                toga.Box(
                    children=[
                        toga.Label(
                            text="No exercises yet",
                            style=Pack(
                                font_size=Theme.FONT_SIZE_SM,
                                color=Theme.TEXT_TERTIARY,
                            ),
                        ),
                    ],
                    style=Pack(
                        padding=Theme.SPACING_LG,
                        alignment=CENTER,
                    ),
                )
            )

        children.append(flex_spacer())

        # Action buttons
        children.append(spacer(Theme.SPACING_LG))
        children.append(self._create_action_buttons())

        return screen_container(children)

    def _create_header(self) -> toga.Box:
        """Create header with back and save buttons."""

        def on_back(widget: toga.Widget) -> None:
            self._save_template()
            self.app.navigate_to_templates()

        def on_save(widget: toga.Widget) -> None:
            self._save_template()

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
                toga.Button(
                    text="Save",
                    on_press=on_save,
                    style=Pack(
                        padding=Theme.SPACING_SM,
                        background_color=Theme.BACKGROUND,
                        color=Theme.SUCCESS,
                        font_size=Theme.FONT_SIZE_BASE,
                    ),
                ),
            ],
            style=Pack(
                direction=ROW,
                padding_bottom=Theme.SPACING_LG,
            ),
        )

    def _save_template(self) -> None:
        """Save template changes."""
        if not self.template:
            return

        # Update name
        if self.name_input and self.name_input.value.strip():
            self.template.name = self.name_input.value.strip()

        self.app.template_repo.save(self.template)

    def _create_add_exercise_button(self) -> toga.Box:
        """Create add exercise button."""

        def on_add(widget: toga.Widget) -> None:
            self._show_add_exercise_dialog()

        return toga.Box(
            children=[
                secondary_button("+ Add Exercise", on_press=on_add),
            ],
            style=Pack(direction=ROW),
        )

    def _show_add_exercise_dialog(self) -> None:
        """Show dialog to add exercise to template."""

        async def add_exercise_dialog(dialog_app: toga.App) -> None:
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
        """Add exercise to template."""
        if not self.template:
            return

        order_index = len(self.template.exercises)
        exercise = TemplateExercise.create(
            template_id=self.template_id,
            name=name,
            order_index=order_index,
            uses_weight=uses_weight,
        )
        self.template.exercises.append(exercise)
        self._save_template()

        # Refresh view
        self.app.navigate_to_template_edit(self.template_id)

    def _create_exercise_item(self, exercise: TemplateExercise) -> toga.Box:
        """Create an exercise list item."""
        weight_text = "" if exercise.uses_weight else " (Bodyweight)"

        def on_toggle_weight(widget: toga.Widget) -> None:
            exercise.uses_weight = not exercise.uses_weight
            self._save_template()
            self.app.navigate_to_template_edit(self.template_id)

        def on_delete(widget: toga.Widget) -> None:
            if self.template:
                self.template.exercises = [
                    ex for ex in self.template.exercises if ex.id != exercise.id
                ]
                # Reorder remaining exercises
                for i, ex in enumerate(self.template.exercises):
                    ex.order_index = i
                self._save_template()
                self.app.navigate_to_template_edit(self.template_id)

        return toga.Box(
            children=[
                toga.Label(
                    text=f"{exercise.name}{weight_text}",
                    style=Pack(
                        font_size=Theme.FONT_SIZE_BASE,
                        color=Theme.TEXT_PRIMARY,
                        flex=1,
                    ),
                ),
                toga.Button(
                    text="BW" if not exercise.uses_weight else "WT",
                    on_press=on_toggle_weight,
                    style=Pack(
                        padding=Theme.SPACING_XS,
                        background_color=Theme.SURFACE_ELEVATED,
                        color=Theme.TEXT_SECONDARY,
                        font_size=Theme.FONT_SIZE_XS,
                        width=40,
                    ),
                ),
                toga.Box(style=Pack(width=Theme.SPACING_SM)),
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

    def _create_action_buttons(self) -> toga.Box:
        """Create template action buttons."""

        def on_start_workout(widget: toga.Widget) -> None:
            self._save_template()
            self._start_workout_from_template()

        def on_duplicate(widget: toga.Widget) -> None:
            if self.template:
                new_template = self.app.template_repo.duplicate(
                    self.template_id,
                    f"{self.template.name} (Copy)",
                )
                if new_template:
                    self.app.navigate_to_template_edit(new_template.id)

        def on_delete(widget: toga.Widget) -> None:
            async def confirm_delete(dialog_app: toga.App) -> None:
                result = await dialog_app.main_window.confirm_dialog(
                    title="Delete Template?",
                    message="This will permanently delete the template.",
                )
                if result:
                    self.app.template_repo.delete(self.template_id)
                    self.app.navigate_to_templates()

            self.app.add_background_task(confirm_delete)

        return toga.Box(
            children=[
                toga.Box(
                    children=[
                        primary_button("Start Workout", on_press=on_start_workout),
                    ],
                    style=Pack(direction=ROW, padding_bottom=Theme.SPACING_SM),
                ),
                toga.Box(
                    children=[
                        toga.Button(
                            text="Duplicate",
                            on_press=on_duplicate,
                            style=Pack(
                                padding=Theme.SPACING_MD,
                                height=Theme.BUTTON_HEIGHT_MD,
                                background_color=Theme.SURFACE,
                                color=Theme.TEXT_PRIMARY,
                                font_size=Theme.FONT_SIZE_BASE,
                                flex=1,
                            ),
                        ),
                        toga.Box(style=Pack(width=Theme.SPACING_SM)),
                        toga.Button(
                            text="Delete",
                            on_press=on_delete,
                            style=Pack(
                                padding=Theme.SPACING_MD,
                                height=Theme.BUTTON_HEIGHT_MD,
                                background_color=Theme.SURFACE,
                                color=Theme.DANGER,
                                font_size=Theme.FONT_SIZE_BASE,
                                flex=1,
                            ),
                        ),
                    ],
                    style=Pack(direction=ROW),
                ),
            ],
            style=Pack(direction=COLUMN),
        )

    def _start_workout_from_template(self) -> None:
        """Start a new workout from this template."""
        if not self.template:
            return

        session = WorkoutSession.create(
            template_id=self.template.id,
            template_name=self.template.name,
        )

        # Add exercises from template
        for tex in self.template.exercises:
            ex = SessionExercise.from_template_exercise(session.id, tex)
            session.exercises.append(ex)
            self.app.session_repo.save_exercise(ex)

        self.app.session_repo.save(session)
        self.app.state_repo.set_active_session_id(session.id)
        self.app.state_repo.set_last_template_id(self.template.id)
        self.app.navigate_to_session(session.id)


def create_template_edit_view(app: "IronLogApp", template_id: UUID) -> toga.Box:
    """Create a template edit view."""
    view = TemplateEditView(app, template_id)
    return view.create_view()
