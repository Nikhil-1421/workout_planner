"""Workout session timer with pause/resume and persistence support."""

from datetime import datetime
from typing import Callable, Optional

from app.core.models import TimerState, format_duration


class Timer:
    """
    Workout session timer with start/pause/resume/stop functionality.

    The timer is designed to be accurate even when the app is backgrounded
    briefly, by storing timestamps rather than incrementing a counter.
    """

    def __init__(
        self,
        on_tick: Optional[Callable[[str], None]] = None,
        on_state_change: Optional[Callable[[TimerState], None]] = None,
    ) -> None:
        """
        Initialize the timer.

        Args:
            on_tick: Callback called every second with formatted time string
            on_state_change: Callback called when timer state changes
        """
        self._state = TimerState.initial()
        self._on_tick = on_tick
        self._on_state_change = on_state_change
        self._tick_task: Optional[object] = None  # Platform-specific timer handle

    @property
    def state(self) -> TimerState:
        """Get current timer state."""
        return self._state

    @property
    def is_running(self) -> bool:
        """Check if timer is running (not paused, not stopped)."""
        return self._state.is_running and not self._state.is_paused

    @property
    def is_paused(self) -> bool:
        """Check if timer is paused."""
        return self._state.is_paused

    @property
    def is_stopped(self) -> bool:
        """Check if timer is stopped (never started or after stop)."""
        return not self._state.is_running

    @property
    def elapsed_seconds(self) -> int:
        """Get total elapsed seconds."""
        return int(self._calculate_elapsed())

    @property
    def formatted_time(self) -> str:
        """Get formatted elapsed time string."""
        return format_duration(self.elapsed_seconds)

    def _calculate_elapsed(self) -> float:
        """Calculate total elapsed time in seconds."""
        if not self._state.is_running:
            return self._state.accumulated_seconds

        if self._state.is_paused:
            # When paused, return accumulated time only
            return self._state.accumulated_seconds

        # When running, add time since last start/resume
        if self._state.start_time is None:
            return self._state.accumulated_seconds

        current_segment = (datetime.now() - self._state.start_time).total_seconds()
        return self._state.accumulated_seconds + current_segment

    def start(self) -> None:
        """Start the timer."""
        if self._state.is_running:
            return

        self._state = TimerState(
            is_running=True,
            is_paused=False,
            start_time=datetime.now(),
            pause_time=None,
            accumulated_seconds=0.0,
        )
        self._notify_state_change()
        self._start_ticking()

    def pause(self) -> None:
        """Pause the timer."""
        if not self._state.is_running or self._state.is_paused:
            return

        # Calculate and store accumulated time
        accumulated = self._calculate_elapsed()

        self._state = TimerState(
            is_running=True,
            is_paused=True,
            start_time=self._state.start_time,
            pause_time=datetime.now(),
            accumulated_seconds=accumulated,
        )
        self._notify_state_change()
        self._stop_ticking()

    def resume(self) -> None:
        """Resume the timer after pause."""
        if not self._state.is_paused:
            return

        self._state = TimerState(
            is_running=True,
            is_paused=False,
            start_time=datetime.now(),  # New start time for this segment
            pause_time=None,
            accumulated_seconds=self._state.accumulated_seconds,
        )
        self._notify_state_change()
        self._start_ticking()

    def stop(self) -> int:
        """
        Stop the timer and return final elapsed seconds.

        Returns:
            Total elapsed seconds
        """
        final_seconds = self.elapsed_seconds
        self._state = TimerState.initial()
        self._notify_state_change()
        self._stop_ticking()
        return final_seconds

    def restore(self, state: TimerState) -> None:
        """
        Restore timer from persisted state.

        Args:
            state: Previously saved timer state
        """
        self._state = state

        # If timer was running (not paused), update start time
        # to account for time passed while app was closed
        if state.is_running and not state.is_paused:
            self._start_ticking()
        elif state.is_running and state.is_paused:
            pass  # Stay paused, no ticking needed

    def _notify_state_change(self) -> None:
        """Notify listener of state change."""
        if self._on_state_change:
            self._on_state_change(self._state)

    def _tick(self) -> None:
        """Called every second to update display."""
        if self._on_tick:
            self._on_tick(self.formatted_time)

    def _start_ticking(self) -> None:
        """Start the tick timer. Override in platform-specific subclass."""
        # This will be handled by the UI layer with platform timers
        pass

    def _stop_ticking(self) -> None:
        """Stop the tick timer. Override in platform-specific subclass."""
        pass


class MockTimer(Timer):
    """Timer subclass for testing without platform dependencies."""

    def __init__(self) -> None:
        super().__init__()
        self._mock_now: Optional[datetime] = None

    def set_mock_time(self, dt: datetime) -> None:
        """Set a mock current time for testing."""
        self._mock_now = dt

    def _calculate_elapsed(self) -> float:
        """Calculate elapsed with mock time support."""
        if self._mock_now is None:
            return super()._calculate_elapsed()

        if not self._state.is_running:
            return self._state.accumulated_seconds

        if self._state.is_paused:
            return self._state.accumulated_seconds

        if self._state.start_time is None:
            return self._state.accumulated_seconds

        current_segment = (self._mock_now - self._state.start_time).total_seconds()
        return self._state.accumulated_seconds + current_segment
