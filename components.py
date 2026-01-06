"""Reusable UI components for IronLog."""

from typing import Callable, Optional

import toga
from toga.style import Pack
from toga.style.pack import BOLD, CENTER, COLUMN, ROW

from app.ui.theme import Theme


def styled_box(
    children: Optional[list] = None,
    direction: str = COLUMN,
    padding: int = 0,
    background: str = Theme.BACKGROUND,
    flex: int = 0,
) -> toga.Box:
    """Create a styled box container."""
    box = toga.Box(
        children=children or [],
        style=Pack(
            direction=direction,
            padding=padding,
            background_color=background,
            flex=flex,
        ),
    )
    return box


def screen_container(children: Optional[list] = None) -> toga.Box:
    """Create a full-screen container with dark background."""
    return toga.Box(
        children=children or [],
        style=Pack(
            direction=COLUMN,
            padding=Theme.SPACING_BASE,
            background_color=Theme.BACKGROUND,
            flex=1,
        ),
    )


def card(children: Optional[list] = None, on_press: Optional[Callable] = None) -> toga.Box:
    """Create a card component."""
    box = toga.Box(
        children=children or [],
        style=Pack(
            direction=COLUMN,
            padding=Theme.CARD_PADDING,
            background_color=Theme.SURFACE,
            flex=0,
        ),
    )
    return box


def spacer(size: int = Theme.SPACING_BASE) -> toga.Box:
    """Create a vertical spacer."""
    return toga.Box(style=Pack(height=size))


def horizontal_spacer(size: int = Theme.SPACING_BASE) -> toga.Box:
    """Create a horizontal spacer."""
    return toga.Box(style=Pack(width=size))


def flex_spacer() -> toga.Box:
    """Create a flexible spacer that expands to fill space."""
    return toga.Box(style=Pack(flex=1))


def title_text(text: str, size: int = Theme.FONT_SIZE_2XL) -> toga.Label:
    """Create a title label."""
    return toga.Label(
        text=text,
        style=Pack(
            font_size=size,
            font_weight=BOLD,
            color=Theme.TEXT_PRIMARY,
            padding_bottom=Theme.SPACING_SM,
        ),
    )


def subtitle_text(text: str) -> toga.Label:
    """Create a subtitle label."""
    return toga.Label(
        text=text,
        style=Pack(
            font_size=Theme.FONT_SIZE_LG,
            color=Theme.TEXT_SECONDARY,
        ),
    )


def body_text(text: str, color: str = Theme.TEXT_PRIMARY) -> toga.Label:
    """Create body text."""
    return toga.Label(
        text=text,
        style=Pack(
            font_size=Theme.FONT_SIZE_BASE,
            color=color,
        ),
    )


def secondary_text(text: str) -> toga.Label:
    """Create secondary/muted text."""
    return toga.Label(
        text=text,
        style=Pack(
            font_size=Theme.FONT_SIZE_SM,
            color=Theme.TEXT_SECONDARY,
        ),
    )


def timer_display(time_str: str = "0:00", color: str = Theme.TIMER) -> toga.Label:
    """Create a large timer display."""
    return toga.Label(
        text=time_str,
        style=Pack(
            font_size=Theme.FONT_SIZE_TIMER,
            font_weight=BOLD,
            color=color,
            text_align=CENTER,
        ),
    )


def primary_button(
    text: str,
    on_press: Optional[Callable] = None,
    enabled: bool = True,
) -> toga.Button:
    """Create a primary action button."""
    return toga.Button(
        text=text,
        on_press=on_press,
        enabled=enabled,
        style=Pack(
            padding=Theme.SPACING_BASE,
            height=Theme.BUTTON_HEIGHT_XL,
            background_color=Theme.PRIMARY if enabled else Theme.SURFACE,
            color=Theme.TEXT_PRIMARY,
            font_size=Theme.FONT_SIZE_LG,
            font_weight=BOLD,
            flex=1,
        ),
    )


def secondary_button(
    text: str,
    on_press: Optional[Callable] = None,
    enabled: bool = True,
) -> toga.Button:
    """Create a secondary action button."""
    return toga.Button(
        text=text,
        on_press=on_press,
        enabled=enabled,
        style=Pack(
            padding=Theme.SPACING_MD,
            height=Theme.BUTTON_HEIGHT_MD,
            background_color=Theme.SURFACE,
            color=Theme.TEXT_PRIMARY,
            font_size=Theme.FONT_SIZE_BASE,
            flex=1,
        ),
    )


def danger_button(
    text: str,
    on_press: Optional[Callable] = None,
) -> toga.Button:
    """Create a danger/destructive button."""
    return toga.Button(
        text=text,
        on_press=on_press,
        style=Pack(
            padding=Theme.SPACING_MD,
            height=Theme.BUTTON_HEIGHT_MD,
            background_color=Theme.DANGER,
            color=Theme.TEXT_PRIMARY,
            font_size=Theme.FONT_SIZE_BASE,
            flex=1,
        ),
    )


def text_button(
    text: str,
    on_press: Optional[Callable] = None,
    color: str = Theme.PRIMARY,
) -> toga.Button:
    """Create a text-only button."""
    return toga.Button(
        text=text,
        on_press=on_press,
        style=Pack(
            padding=Theme.SPACING_SM,
            height=Theme.BUTTON_HEIGHT_SM,
            background_color=Theme.BACKGROUND,
            color=color,
            font_size=Theme.FONT_SIZE_BASE,
        ),
    )


def chip_button(
    text: str,
    on_press: Optional[Callable] = None,
    selected: bool = False,
) -> toga.Button:
    """Create a chip/tag button for quick-add."""
    return toga.Button(
        text=text,
        on_press=on_press,
        style=Pack(
            padding_left=Theme.SPACING_MD,
            padding_right=Theme.SPACING_MD,
            padding_top=Theme.SPACING_SM,
            padding_bottom=Theme.SPACING_SM,
            height=Theme.BUTTON_HEIGHT_SM,
            background_color=Theme.PRIMARY_MUTED if selected else Theme.SURFACE,
            color=Theme.PRIMARY if selected else Theme.TEXT_SECONDARY,
            font_size=Theme.FONT_SIZE_SM,
        ),
    )


def number_input(
    value: str = "",
    placeholder: str = "",
    on_change: Optional[Callable] = None,
) -> toga.TextInput:
    """Create a numeric input field."""
    return toga.TextInput(
        value=value,
        placeholder=placeholder,
        on_change=on_change,
        style=Pack(
            padding=Theme.SPACING_MD,
            height=Theme.BUTTON_HEIGHT_LG,
            background_color=Theme.SURFACE,
            color=Theme.TEXT_PRIMARY,
            font_size=Theme.FONT_SIZE_XL,
            flex=1,
        ),
    )


def text_input(
    value: str = "",
    placeholder: str = "",
    on_change: Optional[Callable] = None,
) -> toga.TextInput:
    """Create a text input field."""
    return toga.TextInput(
        value=value,
        placeholder=placeholder,
        on_change=on_change,
        style=Pack(
            padding=Theme.SPACING_MD,
            height=Theme.BUTTON_HEIGHT_MD,
            background_color=Theme.SURFACE,
            color=Theme.TEXT_PRIMARY,
            font_size=Theme.FONT_SIZE_BASE,
            flex=1,
        ),
    )


def divider() -> toga.Divider:
    """Create a horizontal divider."""
    return toga.Divider(
        style=Pack(
            padding_top=Theme.SPACING_SM,
            padding_bottom=Theme.SPACING_SM,
        )
    )


def row(*children, padding: int = 0, spacing: int = Theme.SPACING_SM) -> toga.Box:
    """Create a horizontal row of items."""
    items = []
    for i, child in enumerate(children):
        items.append(child)
        if i < len(children) - 1 and spacing > 0:
            items.append(horizontal_spacer(spacing))
    return toga.Box(
        children=items,
        style=Pack(
            direction=ROW,
            padding=padding,
            alignment=CENTER,
        ),
    )


def empty_state(title: str, subtitle: str = "") -> toga.Box:
    """Create an empty state display."""
    children = [
        spacer(Theme.SPACING_4XL),
        toga.Label(
            text=title,
            style=Pack(
                font_size=Theme.FONT_SIZE_LG,
                color=Theme.TEXT_TERTIARY,
                text_align=CENTER,
            ),
        ),
    ]
    if subtitle:
        children.append(spacer(Theme.SPACING_SM))
        children.append(
            toga.Label(
                text=subtitle,
                style=Pack(
                    font_size=Theme.FONT_SIZE_SM,
                    color=Theme.TEXT_TERTIARY,
                    text_align=CENTER,
                ),
            )
        )
    children.append(flex_spacer())

    return toga.Box(
        children=children,
        style=Pack(
            direction=COLUMN,
            alignment=CENTER,
            flex=1,
            padding=Theme.SPACING_XL,
        ),
    )


def list_item(
    title: str,
    subtitle: str = "",
    right_text: str = "",
    on_press: Optional[Callable] = None,
) -> toga.Box:
    """Create a list item row."""
    left_content = [
        toga.Label(
            text=title,
            style=Pack(
                font_size=Theme.FONT_SIZE_BASE,
                color=Theme.TEXT_PRIMARY,
            ),
        ),
    ]
    if subtitle:
        left_content.append(
            toga.Label(
                text=subtitle,
                style=Pack(
                    font_size=Theme.FONT_SIZE_SM,
                    color=Theme.TEXT_SECONDARY,
                    padding_top=Theme.SPACING_XS,
                ),
            )
        )

    left_box = toga.Box(
        children=left_content,
        style=Pack(direction=COLUMN, flex=1),
    )

    children = [left_box]

    if right_text:
        children.append(
            toga.Label(
                text=right_text,
                style=Pack(
                    font_size=Theme.FONT_SIZE_SM,
                    color=Theme.TEXT_SECONDARY,
                ),
            )
        )

    # Add chevron indicator
    children.append(
        toga.Label(
            text="›",
            style=Pack(
                font_size=Theme.FONT_SIZE_XL,
                color=Theme.TEXT_TERTIARY,
                padding_left=Theme.SPACING_SM,
            ),
        )
    )

    return toga.Box(
        children=children,
        style=Pack(
            direction=ROW,
            padding=Theme.SPACING_BASE,
            background_color=Theme.SURFACE,
            alignment=CENTER,
        ),
    )


def header_bar(
    title: str,
    left_button: Optional[toga.Button] = None,
    right_button: Optional[toga.Button] = None,
) -> toga.Box:
    """Create a header bar with optional navigation buttons."""
    children = []

    if left_button:
        children.append(left_button)
    else:
        children.append(toga.Box(style=Pack(width=60)))  # Placeholder for alignment

    children.append(flex_spacer())
    children.append(
        toga.Label(
            text=title,
            style=Pack(
                font_size=Theme.FONT_SIZE_LG,
                font_weight=BOLD,
                color=Theme.TEXT_PRIMARY,
            ),
        )
    )
    children.append(flex_spacer())

    if right_button:
        children.append(right_button)
    else:
        children.append(toga.Box(style=Pack(width=60)))  # Placeholder for alignment

    return toga.Box(
        children=children,
        style=Pack(
            direction=ROW,
            padding=Theme.SPACING_SM,
            background_color=Theme.BACKGROUND,
            alignment=CENTER,
            height=Theme.TAP_TARGET_MIN,
        ),
    )
