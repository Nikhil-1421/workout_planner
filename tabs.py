"""Tab bar navigation for IronLog."""

from typing import TYPE_CHECKING, Callable, Optional

import toga
from toga.style import Pack
from toga.style.pack import BOLD, CENTER, COLUMN, ROW

from app.ui.theme import Theme

if TYPE_CHECKING:
    from app.main import IronLogApp


class TabItem:
    """Represents a single tab in the tab bar."""

    def __init__(
        self,
        name: str,
        icon: str,
        create_content: Callable[[], toga.Box],
    ) -> None:
        self.name = name
        self.icon = icon
        self.create_content = create_content
        self.content: Optional[toga.Box] = None
        self.button: Optional[toga.Button] = None


class TabBar(toga.Box):
    """
    A sleek, minimal tab bar navigation component.

    Features:
    - Dark background matching theme
    - Clear selected state
    - Minimal labels
    - Consistent spacing
    """

    def __init__(
        self,
        app: "IronLogApp",
        tabs: list[TabItem],
        on_tab_change: Optional[Callable[[int], None]] = None,
    ) -> None:
        super().__init__(style=Pack(direction=COLUMN, flex=1))

        self.app = app
        self.tabs = tabs
        self.on_tab_change = on_tab_change
        self.current_index = 0

        # Content area (fills remaining space)
        self.content_area = toga.Box(
            style=Pack(
                direction=COLUMN,
                flex=1,
                background_color=Theme.BACKGROUND,
            )
        )

        # Tab bar at bottom
        self.tab_bar = toga.Box(
            style=Pack(
                direction=ROW,
                background_color=Theme.SURFACE,
                padding_top=Theme.SPACING_SM,
                padding_bottom=Theme.SPACING_SM,
                alignment=CENTER,
            )
        )

        # Create tab buttons
        for i, tab in enumerate(self.tabs):
            tab.button = self._create_tab_button(i, tab)
            self.tab_bar.add(tab.button)

        # Add border on top of tab bar
        tab_bar_container = toga.Box(
            children=[
                toga.Divider(
                    style=Pack(background_color=Theme.BORDER)
                ),
                self.tab_bar,
            ],
            style=Pack(direction=COLUMN),
        )

        self.add(self.content_area)
        self.add(tab_bar_container)

        # Initialize first tab
        self.select_tab(0)

    def _create_tab_button(self, index: int, tab: TabItem) -> toga.Button:
        """Create a tab bar button."""

        def on_press(widget: toga.Widget) -> None:
            self.select_tab(index)

        btn = toga.Button(
            text=f"{tab.icon}\n{tab.name}",
            on_press=on_press,
            style=Pack(
                flex=1,
                padding=Theme.SPACING_XS,
                background_color=Theme.SURFACE,
                color=Theme.TEXT_TERTIARY,
                font_size=Theme.FONT_SIZE_XS,
                text_align=CENTER,
            ),
        )
        return btn

    def select_tab(self, index: int) -> None:
        """Select a tab by index."""
        if index < 0 or index >= len(self.tabs):
            return

        # Update button states
        for i, tab in enumerate(self.tabs):
            if tab.button:
                if i == index:
                    tab.button.style.color = Theme.PRIMARY
                    tab.button.style.font_weight = BOLD
                else:
                    tab.button.style.color = Theme.TEXT_TERTIARY
                    tab.button.style.font_weight = "normal"

        # Update content
        self.current_index = index
        tab = self.tabs[index]

        # Create content if not already created
        if tab.content is None:
            tab.content = tab.create_content()

        # Clear and set new content
        self.content_area.clear()
        self.content_area.add(tab.content)

        # Notify listener
        if self.on_tab_change:
            self.on_tab_change(index)

    def refresh_current_tab(self) -> None:
        """Refresh the current tab's content."""
        tab = self.tabs[self.current_index]
        tab.content = tab.create_content()
        self.content_area.clear()
        self.content_area.add(tab.content)

    def navigate_to(self, tab_name: str) -> None:
        """Navigate to a tab by name."""
        for i, tab in enumerate(self.tabs):
            if tab.name.lower() == tab_name.lower():
                self.select_tab(i)
                return


def create_tab_bar(app: "IronLogApp") -> TabBar:
    """Create the main tab bar with all tabs."""
    from app.ui.history import create_history_tab
    from app.ui.home import create_home_tab
    from app.ui.settings import create_settings_tab
    from app.ui.templates import create_templates_tab

    tabs = [
        TabItem(
            name="Home",
            icon="🏠",
            create_content=lambda: create_home_tab(app),
        ),
        TabItem(
            name="Templates",
            icon="📋",
            create_content=lambda: create_templates_tab(app),
        ),
        TabItem(
            name="History",
            icon="📊",
            create_content=lambda: create_history_tab(app),
        ),
        TabItem(
            name="Settings",
            icon="⚙️",
            create_content=lambda: create_settings_tab(app),
        ),
    ]

    return TabBar(app, tabs)
