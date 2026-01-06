"""Theme constants for IronLog - Dark, minimal, premium aesthetic."""


class Theme:
    """
    Design system for IronLog.

    Dark theme with high contrast, minimal color palette,
    and generous spacing for a premium feel.
    """

    # ==========================================================================
    # COLORS - Dark theme palette
    # ==========================================================================

    # Backgrounds (darkest to lighter)
    BACKGROUND = "#0D0D0D"  # Main background - near black
    SURFACE = "#1A1A1A"  # Cards, elevated surfaces
    SURFACE_ELEVATED = "#242424"  # Modals, sheets
    SURFACE_HOVER = "#2A2A2A"  # Hover states

    # Borders
    BORDER = "#333333"  # Subtle borders
    BORDER_FOCUS = "#4A4A4A"  # Focus states

    # Text
    TEXT_PRIMARY = "#FFFFFF"  # Primary text
    TEXT_SECONDARY = "#A0A0A0"  # Secondary text
    TEXT_TERTIARY = "#666666"  # Placeholder, disabled
    TEXT_INVERSE = "#0D0D0D"  # Text on light backgrounds

    # Primary accent - Electric blue
    PRIMARY = "#3B82F6"  # Primary actions
    PRIMARY_HOVER = "#2563EB"  # Primary hover
    PRIMARY_MUTED = "#1E3A5F"  # Primary background tint

    # Secondary accent - Success green
    SUCCESS = "#22C55E"  # Success states, completed
    SUCCESS_MUTED = "#14532D"  # Success background

    # Warning / caution
    WARNING = "#F59E0B"  # Warning states
    WARNING_MUTED = "#78350F"  # Warning background

    # Danger / destructive
    DANGER = "#EF4444"  # Destructive actions
    DANGER_HOVER = "#DC2626"  # Danger hover
    DANGER_MUTED = "#7F1D1D"  # Danger background

    # Timer accent - Vibrant cyan for active timer
    TIMER = "#06B6D4"  # Timer display
    TIMER_PAUSED = "#F59E0B"  # Paused timer

    # ==========================================================================
    # TYPOGRAPHY
    # ==========================================================================

    # Font sizes (in points)
    FONT_SIZE_XS = 11
    FONT_SIZE_SM = 13
    FONT_SIZE_BASE = 15
    FONT_SIZE_LG = 17
    FONT_SIZE_XL = 20
    FONT_SIZE_2XL = 24
    FONT_SIZE_3XL = 30
    FONT_SIZE_4XL = 36
    FONT_SIZE_TIMER = 48  # Large timer display

    # ==========================================================================
    # SPACING (in pixels)
    # ==========================================================================

    SPACING_XS = 4
    SPACING_SM = 8
    SPACING_MD = 12
    SPACING_BASE = 16
    SPACING_LG = 20
    SPACING_XL = 24
    SPACING_2XL = 32
    SPACING_3XL = 40
    SPACING_4XL = 48

    # ==========================================================================
    # SIZING
    # ==========================================================================

    # Minimum tap target size (iOS HIG recommends 44pt)
    TAP_TARGET_MIN = 44

    # Button heights
    BUTTON_HEIGHT_SM = 36
    BUTTON_HEIGHT_MD = 44
    BUTTON_HEIGHT_LG = 52
    BUTTON_HEIGHT_XL = 60  # Primary action buttons

    # Border radius
    RADIUS_SM = 6
    RADIUS_MD = 8
    RADIUS_LG = 12
    RADIUS_XL = 16
    RADIUS_FULL = 9999  # Fully rounded

    # Card dimensions
    CARD_PADDING = 16
    CARD_RADIUS = 12

    # ==========================================================================
    # QUICK-ADD CHIP DEFAULTS
    # ==========================================================================

    # Common rep values for quick-add
    QUICK_REPS = [5, 8, 10, 12]

    # Weight increments for quick-add
    WEIGHT_INCREMENT_SMALL = 5
    WEIGHT_INCREMENT_LARGE = 10

    # ==========================================================================
    # EMPTY STATE MESSAGES
    # ==========================================================================

    EMPTY_TEMPLATES = "No templates yet"
    EMPTY_TEMPLATES_HINT = "Create your first workout template"
    EMPTY_HISTORY = "No workouts yet"
    EMPTY_HISTORY_HINT = "Start your first workout"
    EMPTY_EXERCISES = "No exercises"
    EMPTY_EXERCISES_HINT = "Add an exercise to get started"
    EMPTY_SETS = "No sets logged"
    EMPTY_SETS_HINT = "Log your first set"
