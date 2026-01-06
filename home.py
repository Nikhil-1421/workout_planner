"""Home tab - Quick start workout."""

from typing import TYPE_CHECKING, Optional
from uuid import UUID

import toga
from toga.style import Pack
from toga.style.pack import BOLD, CENTER, COLUMN, ROW

from app.core.models import WorkoutSession, WorkoutTemplate
from app.ui.components import (
    body_text,
    card,
    empty_state,
    flex_spacer,
    primary_button,
    screen_container,
    secondary_button,
    secondary_text,
    spacer,
    title_text,
)
from app.ui.theme import Theme

if TYPE_CHECKING:
    from app.main import IronLogApp


def create_home_tab(app: "IronLogApp") -> toga.Box:
    """Create the Home tab content."""
    # Check for active session
    active_session = app.session_repo.get_active()

    # Get templates for selection
    templates = app.template_repo.get_all()

    # Get last used template
    last_template_id = app.state_repo.get_last_template_id()
    last_template: Optional[WorkoutTemplate] = None
    if last_template_id:
        last_template = app.template_repo.get_by_id(last_template_id)

    # Build content
    children = [
        # Header
        toga.Box(
            children=[
                title_text("IronLog", size=Theme.FONT_SIZE_3XL),
                secondary_text("Track your workouts"),
            ],
            style=Pack(direction=COLUMN, padding_bottom=Theme.SPACING_2XL),
        ),
    ]

    # Active session card (if exists)
    if active_session:
        children.append(_active_session_card(app, active_session))
        children.append(spacer(Theme.SPACING_XL))
    else:
        # Quick start section
        children.append(_quick_start_section(app, templates, last_template))

    children.append(flex_spacer())

    # Stats summary (if any history exists)
    sessions = app.session_repo.get_all(limit=7)
    if sessions:
        children.append(_recent_stats(sessions))

    return screen_container(children)


def _active_session_card(app: "IronLogApp", session: WorkoutSession) -> toga.Box:
    """Create card for continuing active session."""

    def on_continue(widget: toga.Widget) -> None:
        app.navigate_to_session(session.id)

    def on_discard(widget: toga.Widget) -> None:
        async def confirm_discard(dialog_app: toga.App) -> None:
            result = await dialog_app.main_window.confirm_dialog(
                title="Discard Workout?",
                message="This will delete the current workout. This cannot be undone.",
            )
            if result:
                app.session_repo.delete(session.id)
                app.state_repo.set_active_session_id(None)
                app.state_repo.set_timer_state(None)
                app.refresh_home()

        app.add_background_task(confirm_discard)

    template_name = session.template_name or "Custom Workout"
    exercise_count = len(session.exercises)
    set_count = session.total_sets

    return toga.Box(
        children=[
            toga.Box(
                children=[
                    toga.Label(
                        text="🔥 Active Workout",
                        style=Pack(
                            font_size=Theme.FONT_SIZE_SM,
                            color=Theme.WARNING,
                            font_weight=BOLD,
                        ),
                    ),
                    spacer(Theme.SPACING_SM),
                    toga.Label(
                        text=template_name,
                        style=Pack(
                            font_size=Theme.FONT_SIZE_XL,
                            color=Theme.TEXT_PRIMARY,
                            font_weight=BOLD,
                        ),
                    ),
                    spacer(Theme.SPACING_XS),
                    toga.Label(
                        text=f"{exercise_count} exercises · {set_count} sets logged",
                        style=Pack(
                            font_size=Theme.FONT_SIZE_SM,
                            color=Theme.TEXT_SECONDARY,
                        ),
                    ),
                ],
                style=Pack(direction=COLUMN),
            ),
            spacer(Theme.SPACING_LG),
            primary_button("Continue Workout", on_press=on_continue),
            spacer(Theme.SPACING_SM),
            toga.Button(
                text="Discard",
                on_press=on_discard,
                style=Pack(
                    padding=Theme.SPACING_SM,
                    background_color=Theme.SURFACE,
                    color=Theme.DANGER,
                    font_size=Theme.FONT_SIZE_SM,
                ),
            ),
        ],
        style=Pack(
            direction=COLUMN,
            padding=Theme.CARD_PADDING,
            background_color=Theme.SURFACE,
        ),
    )


def _quick_start_section(
    app: "IronLogApp",
    templates: list[WorkoutTemplate],
    last_template: Optional[WorkoutTemplate],
) -> toga.Box:
    """Create the quick start workout section."""

    def start_empty_workout(widget: toga.Widget) -> None:
        session = WorkoutSession.create()
        app.session_repo.save(session)
        app.state_repo.set_active_session_id(session.id)
        app.navigate_to_session(session.id)

    def start_with_template(template: WorkoutTemplate) -> None:
        session = WorkoutSession.create(
            template_id=template.id,
            template_name=template.name,
        )
        # Add exercises from template
        from app.core.models import SessionExercise

        for tex in template.exercises:
            ex = SessionExercise.from_template_exercise(session.id, tex)
            session.exercises.append(ex)
            app.session_repo.save_exercise(ex)

        app.session_repo.save(session)
        app.state_repo.set_active_session_id(session.id)
        app.state_repo.set_last_template_id(template.id)
        app.navigate_to_session(session.id)

    children = []

    # Main start button
    children.append(
        toga.Box(
            children=[
                primary_button("Start Empty Workout", on_press=start_empty_workout),
            ],
            style=Pack(direction=COLUMN),
        )
    )

    children.append(spacer(Theme.SPACING_XL))

    # Last used template (if any)
    if last_template:
        children.append(
            toga.Label(
                text="Quick Start",
                style=Pack(
                    font_size=Theme.FONT_SIZE_SM,
                    color=Theme.TEXT_SECONDARY,
                    padding_bottom=Theme.SPACING_SM,
                ),
            )
        )

        def on_last_template(widget: toga.Widget) -> None:
            start_with_template(last_template)

        children.append(
            toga.Box(
                children=[
                    secondary_button(
                        f"▶ {last_template.name}",
                        on_press=on_last_template,
                    ),
                ],
                style=Pack(direction=COLUMN),
            )
        )
        children.append(spacer(Theme.SPACING_LG))

    # Template picker
    if templates:
        children.append(
            toga.Label(
                text="Choose Template",
                style=Pack(
                    font_size=Theme.FONT_SIZE_SM,
                    color=Theme.TEXT_SECONDARY,
                    padding_bottom=Theme.SPACING_SM,
                ),
            )
        )

        for template in templates[:5]:  # Show max 5 templates

            def on_template_press(widget: toga.Widget, t: WorkoutTemplate = template) -> None:
                start_with_template(t)

            children.append(
                toga.Box(
                    children=[
                        toga.Button(
                            text=template.name,
                            on_press=on_template_press,
                            style=Pack(
                                padding=Theme.SPACING_MD,
                                background_color=Theme.SURFACE,
                                color=Theme.TEXT_PRIMARY,
                                font_size=Theme.FONT_SIZE_BASE,
                                flex=1,
                                text_align=CENTER,
                            ),
                        ),
                    ],
                    style=Pack(direction=ROW, padding_bottom=Theme.SPACING_SM),
                )
            )
    else:
        # No templates yet
        children.append(
            toga.Box(
                children=[
                    toga.Label(
                        text="No templates yet",
                        style=Pack(
                            font_size=Theme.FONT_SIZE_SM,
                            color=Theme.TEXT_TERTIARY,
                        ),
                    ),
                    toga.Label(
                        text="Create templates in the Templates tab",
                        style=Pack(
                            font_size=Theme.FONT_SIZE_XS,
                            color=Theme.TEXT_TERTIARY,
                            padding_top=Theme.SPACING_XS,
                        ),
                    ),
                ],
                style=Pack(
                    direction=COLUMN,
                    alignment=CENTER,
                    padding=Theme.SPACING_LG,
                ),
            )
        )

    return toga.Box(
        children=children,
        style=Pack(direction=COLUMN),
    )


def _recent_stats(sessions: list[WorkoutSession]) -> toga.Box:
    """Create recent stats summary."""
    # Count sessions this week
    from datetime import datetime, timedelta

    week_ago = datetime.now() - timedelta(days=7)
    week_sessions = [s for s in sessions if s.started_at >= week_ago]

    total_sets = sum(s.total_sets for s in week_sessions)
    total_reps = sum(s.total_reps for s in week_sessions)

    return toga.Box(
        children=[
            toga.Label(
                text="This Week",
                style=Pack(
                    font_size=Theme.FONT_SIZE_SM,
                    color=Theme.TEXT_TERTIARY,
                    padding_bottom=Theme.SPACING_SM,
                ),
            ),
            toga.Box(
                children=[
                    _stat_item(str(len(week_sessions)), "workouts"),
                    _stat_item(str(total_sets), "sets"),
                    _stat_item(str(total_reps), "reps"),
                ],
                style=Pack(direction=ROW),
            ),
        ],
        style=Pack(
            direction=COLUMN,
            padding=Theme.SPACING_BASE,
            background_color=Theme.SURFACE,
        ),
    )


def _stat_item(value: str, label: str) -> toga.Box:
    """Create a single stat display."""
    return toga.Box(
        children=[
            toga.Label(
                text=value,
                style=Pack(
                    font_size=Theme.FONT_SIZE_2XL,
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
