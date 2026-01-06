"""IronLog - Main Application Entry Point."""

import asyncio
from typing import Optional
from uuid import UUID

import toga
from toga.style import Pack
from toga.style.pack import COLUMN

from app.data.db import Database
from app.data.repositories import AppStateRepository, SessionRepository, TemplateRepository
from app.ui.tabs import TabBar, create_tab_bar
from app.ui.theme import Theme


class IronLogApp(toga.App):
    """
    IronLog - Premium Workout Tracker

    A sleek, dark-themed, minimalist workout tracker with:
    - Workout Templates
    - Session Timer
    - Per-exercise logging
    - Offline-first persistence
    - History view
    - Export (JSON + CSV)
    """

    def __init__(self) -> None:
        super().__init__(
            formal_name="IronLog",
            app_id="app.ironlog.workout",
            app_name="ironlog",
        )

        # Database and repositories
        self.db: Optional[Database] = None
        self.template_repo: Optional[TemplateRepository] = None
        self.session_repo: Optional[SessionRepository] = None
        self.state_repo: Optional[AppStateRepository] = None

        # UI state
        self.tab_bar: Optional[TabBar] = None
        self.main_content: Optional[toga.Box] = None
        self.navigation_stack: list = []

    def startup(self) -> None:
        """Initialize the application."""
        # Initialize database
        self.db = Database.get_instance()
        self.db.initialize()

        # Initialize repositories
        self.template_repo = TemplateRepository(self.db)
        self.session_repo = SessionRepository(self.db)
        self.state_repo = AppStateRepository(self.db)

        # Create main window
        self.main_window = toga.MainWindow(
            title="IronLog",
            size=(390, 844),  # iPhone-like dimensions
        )

        # Create main content container
        self.main_content = toga.Box(
            style=Pack(
                direction=COLUMN,
                flex=1,
                background_color=Theme.BACKGROUND,
            )
        )

        # Create tab bar navigation
        self.tab_bar = create_tab_bar(self)
        self.main_content.add(self.tab_bar)

        # Set main content
        self.main_window.content = self.main_content

        # Show window
        self.main_window.show()

    # =========================================================================
    # Navigation Methods
    # =========================================================================

    def navigate_home(self) -> None:
        """Navigate to home tab."""
        self._show_tab_bar()
        self.tab_bar.select_tab(0)

    def refresh_home(self) -> None:
        """Refresh home tab content."""
        if self.tab_bar and self.tab_bar.current_index == 0:
            self.tab_bar.refresh_current_tab()

    def navigate_to_templates(self) -> None:
        """Navigate to templates tab."""
        self._show_tab_bar()
        self.tab_bar.select_tab(1)
        self.tab_bar.refresh_current_tab()

    def navigate_to_history(self) -> None:
        """Navigate to history tab."""
        self._show_tab_bar()
        self.tab_bar.select_tab(2)
        self.tab_bar.refresh_current_tab()

    def navigate_to_session(self, session_id: UUID) -> None:
        """Navigate to active session view."""
        from app.ui.session import create_session_view

        self._hide_tab_bar()
        view = create_session_view(self, session_id)
        self._push_view(view)

    def navigate_to_exercise(self, session_id: UUID, exercise_id: UUID) -> None:
        """Navigate to exercise detail view."""
        from app.ui.exercise_detail import create_exercise_detail_view

        self._hide_tab_bar()
        view = create_exercise_detail_view(self, session_id, exercise_id)
        self._push_view(view)

    def navigate_to_template_edit(self, template_id: UUID) -> None:
        """Navigate to template edit view."""
        from app.ui.templates import create_template_edit_view

        self._hide_tab_bar()
        view = create_template_edit_view(self, template_id)
        self._push_view(view)

    def navigate_to_session_detail(self, session_id: UUID) -> None:
        """Navigate to session detail (read-only history view)."""
        from app.ui.history import create_session_detail_view

        self._hide_tab_bar()
        view = create_session_detail_view(self, session_id)
        self._push_view(view)

    def _show_tab_bar(self) -> None:
        """Show the tab bar navigation."""
        self.main_content.clear()
        self.main_content.add(self.tab_bar)
        self.navigation_stack.clear()

    def _hide_tab_bar(self) -> None:
        """Hide the tab bar and prepare for pushed view."""
        pass  # Tab bar is replaced by pushed view

    def _push_view(self, view: toga.Box) -> None:
        """Push a view onto the navigation stack."""
        self.main_content.clear()
        self.main_content.add(view)
        self.navigation_stack.append(view)

    def _pop_view(self) -> None:
        """Pop the current view and go back."""
        if self.navigation_stack:
            self.navigation_stack.pop()
            if self.navigation_stack:
                self.main_content.clear()
                self.main_content.add(self.navigation_stack[-1])
            else:
                self._show_tab_bar()


def main() -> toga.App:
    """Application factory function."""
    return IronLogApp()


if __name__ == "__main__":
    app = main()
    app.main_loop()
