"""Settings tab - Export, app info, and reset."""

from pathlib import Path
from typing import TYPE_CHECKING, Optional

import toga
from toga.style import Pack
from toga.style.pack import BOLD, CENTER, COLUMN, ROW

from app import __version__
from app.core.export import (
    export_session_csv,
    export_session_json,
    generate_export_filename,
)
from app.core.models import WorkoutSession
from app.ui.components import (
    danger_button,
    flex_spacer,
    screen_container,
    secondary_button,
    spacer,
    title_text,
)
from app.ui.theme import Theme

if TYPE_CHECKING:
    from app.main import IronLogApp


def create_settings_tab(app: "IronLogApp") -> toga.Box:
    """Create the Settings tab content."""
    children = [
        # Header
        title_text("Settings"),
        spacer(Theme.SPACING_LG),
    ]

    # Export section
    children.append(_create_export_section(app))
    children.append(spacer(Theme.SPACING_2XL))

    # App info section
    children.append(_create_app_info_section())
    children.append(spacer(Theme.SPACING_2XL))

    # Danger zone
    children.append(_create_danger_zone(app))

    children.append(flex_spacer())

    return screen_container(children)


def _create_export_section(app: "IronLogApp") -> toga.Box:
    """Create export tools section."""
    sessions = app.session_repo.get_all(limit=20)
    completed_sessions = [s for s in sessions if s.ended_at is not None]

    children = [
        toga.Label(
            text="Export Data",
            style=Pack(
                font_size=Theme.FONT_SIZE_LG,
                font_weight=BOLD,
                color=Theme.TEXT_PRIMARY,
                padding_bottom=Theme.SPACING_SM,
            ),
        ),
        toga.Label(
            text="Export your workout data as JSON or CSV files.",
            style=Pack(
                font_size=Theme.FONT_SIZE_SM,
                color=Theme.TEXT_SECONDARY,
                padding_bottom=Theme.SPACING_LG,
            ),
        ),
    ]

    if completed_sessions:
        # Session selector
        children.append(
            toga.Label(
                text="Select Session to Export",
                style=Pack(
                    font_size=Theme.FONT_SIZE_SM,
                    color=Theme.TEXT_SECONDARY,
                    padding_bottom=Theme.SPACING_SM,
                ),
            )
        )

        # List recent sessions with export buttons
        for session in completed_sessions[:5]:
            children.append(_create_export_row(app, session))
            children.append(spacer(Theme.SPACING_SM))
    else:
        children.append(
            toga.Label(
                text="No completed workouts to export yet.",
                style=Pack(
                    font_size=Theme.FONT_SIZE_SM,
                    color=Theme.TEXT_TERTIARY,
                ),
            )
        )

    return toga.Box(
        children=children,
        style=Pack(direction=COLUMN),
    )


def _create_export_row(app: "IronLogApp", session: WorkoutSession) -> toga.Box:
    """Create an export row for a session."""
    name = session.template_name or "Custom Workout"
    date_str = session.started_at.strftime("%b %d")

    def on_export_json(widget: toga.Widget) -> None:
        _export_session(app, session, "json")

    def on_export_csv(widget: toga.Widget) -> None:
        _export_session(app, session, "csv")

    return toga.Box(
        children=[
            toga.Label(
                text=f"{name} ({date_str})",
                style=Pack(
                    font_size=Theme.FONT_SIZE_SM,
                    color=Theme.TEXT_PRIMARY,
                    flex=1,
                ),
            ),
            toga.Button(
                text="JSON",
                on_press=on_export_json,
                style=Pack(
                    padding=Theme.SPACING_XS,
                    background_color=Theme.SURFACE,
                    color=Theme.PRIMARY,
                    font_size=Theme.FONT_SIZE_XS,
                ),
            ),
            toga.Box(style=Pack(width=Theme.SPACING_SM)),
            toga.Button(
                text="CSV",
                on_press=on_export_csv,
                style=Pack(
                    padding=Theme.SPACING_XS,
                    background_color=Theme.SURFACE,
                    color=Theme.PRIMARY,
                    font_size=Theme.FONT_SIZE_XS,
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


def _export_session(app: "IronLogApp", session: WorkoutSession, format_type: str) -> None:
    """Export a session to file."""
    # Get export directory
    export_dir = Path.home() / ".ironlog" / "exports"
    export_dir.mkdir(parents=True, exist_ok=True)

    filename = generate_export_filename(session, format_type)
    filepath = export_dir / filename

    try:
        if format_type == "json":
            export_session_json(session, filepath)
        else:
            export_session_csv(session, filepath)

        # Show success message
        async def show_success(dialog_app: toga.App) -> None:
            await dialog_app.main_window.info_dialog(
                title="Export Successful",
                message=f"File saved to:\n{filepath}",
            )

        app.add_background_task(show_success)

    except Exception as e:
        # Show error message
        async def show_error(dialog_app: toga.App) -> None:
            await dialog_app.main_window.error_dialog(
                title="Export Failed",
                message=f"Could not export file: {str(e)}",
            )

        app.add_background_task(show_error)


def _create_app_info_section() -> toga.Box:
    """Create app info section."""
    return toga.Box(
        children=[
            toga.Label(
                text="About IronLog",
                style=Pack(
                    font_size=Theme.FONT_SIZE_LG,
                    font_weight=BOLD,
                    color=Theme.TEXT_PRIMARY,
                    padding_bottom=Theme.SPACING_SM,
                ),
            ),
            toga.Box(
                children=[
                    toga.Label(
                        text="Version",
                        style=Pack(
                            font_size=Theme.FONT_SIZE_SM,
                            color=Theme.TEXT_SECONDARY,
                            flex=1,
                        ),
                    ),
                    toga.Label(
                        text=__version__,
                        style=Pack(
                            font_size=Theme.FONT_SIZE_SM,
                            color=Theme.TEXT_PRIMARY,
                        ),
                    ),
                ],
                style=Pack(
                    direction=ROW,
                    padding=Theme.SPACING_SM,
                    background_color=Theme.SURFACE,
                ),
            ),
            spacer(Theme.SPACING_XS),
            toga.Box(
                children=[
                    toga.Label(
                        text="Built with",
                        style=Pack(
                            font_size=Theme.FONT_SIZE_SM,
                            color=Theme.TEXT_SECONDARY,
                            flex=1,
                        ),
                    ),
                    toga.Label(
                        text="Python + BeeWare",
                        style=Pack(
                            font_size=Theme.FONT_SIZE_SM,
                            color=Theme.TEXT_PRIMARY,
                        ),
                    ),
                ],
                style=Pack(
                    direction=ROW,
                    padding=Theme.SPACING_SM,
                    background_color=Theme.SURFACE,
                ),
            ),
        ],
        style=Pack(direction=COLUMN),
    )


def _create_danger_zone(app: "IronLogApp") -> toga.Box:
    """Create danger zone section with reset button."""

    def on_reset(widget: toga.Widget) -> None:
        async def confirm_reset(dialog_app: toga.App) -> None:
            result = await dialog_app.main_window.confirm_dialog(
                title="Reset All Data?",
                message="This will permanently delete all workouts, templates, and settings. This cannot be undone!",
            )
            if result:
                # Double confirm
                result2 = await dialog_app.main_window.confirm_dialog(
                    title="Are you sure?",
                    message="All your data will be permanently deleted.",
                )
                if result2:
                    _reset_all_data(app)

        app.add_background_task(confirm_reset)

    return toga.Box(
        children=[
            toga.Label(
                text="Danger Zone",
                style=Pack(
                    font_size=Theme.FONT_SIZE_LG,
                    font_weight=BOLD,
                    color=Theme.DANGER,
                    padding_bottom=Theme.SPACING_SM,
                ),
            ),
            toga.Label(
                text="These actions are permanent and cannot be undone.",
                style=Pack(
                    font_size=Theme.FONT_SIZE_SM,
                    color=Theme.TEXT_SECONDARY,
                    padding_bottom=Theme.SPACING_LG,
                ),
            ),
            toga.Box(
                children=[
                    danger_button("Reset All Data", on_press=on_reset),
                ],
                style=Pack(direction=ROW),
            ),
        ],
        style=Pack(direction=COLUMN),
    )


def _reset_all_data(app: "IronLogApp") -> None:
    """Reset all app data."""
    try:
        app.db.reset()
        app.db.initialize()

        # Show success
        async def show_success(dialog_app: toga.App) -> None:
            await dialog_app.main_window.info_dialog(
                title="Data Reset",
                message="All data has been deleted. The app will now restart.",
            )
            # Refresh to home tab
            app.tab_bar.select_tab(0)

        app.add_background_task(show_success)

    except Exception as e:
        async def show_error(dialog_app: toga.App) -> None:
            await dialog_app.main_window.error_dialog(
                title="Reset Failed",
                message=f"Could not reset data: {str(e)}",
            )

        app.add_background_task(show_error)
