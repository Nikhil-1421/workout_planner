"""Tests for the Timer module."""

from datetime import datetime, timedelta

import pytest

from app.core.timer import MockTimer, Timer
from app.core.models import TimerState


class TestTimer:
    """Test cases for the Timer class."""

    def test_timer_starts_at_zero(self) -> None:
        """Timer should start with zero elapsed time."""
        timer = Timer()
        assert timer.elapsed_seconds == 0
        assert timer.is_stopped

    def test_timer_starts(self) -> None:
        """Timer should start running when start() is called."""
        timer = Timer()
        timer.start()
        assert timer.is_running
        assert not timer.is_paused
        assert not timer.is_stopped

    def test_timer_pause(self) -> None:
        """Timer should pause correctly."""
        timer = Timer()
        timer.start()
        timer.pause()
        assert timer.is_paused
        assert not timer.is_running  # is_running returns False when paused

    def test_timer_resume(self) -> None:
        """Timer should resume after pause."""
        timer = Timer()
        timer.start()
        timer.pause()
        timer.resume()
        assert timer.is_running
        assert not timer.is_paused

    def test_timer_stop(self) -> None:
        """Timer should stop and return elapsed time."""
        timer = MockTimer()
        timer.start()

        # Simulate time passing
        start_time = timer.state.start_time
        timer.set_mock_time(start_time + timedelta(seconds=60))

        elapsed = timer.stop()
        assert elapsed == 60
        assert timer.is_stopped

    def test_timer_elapsed_during_pause(self) -> None:
        """Elapsed time should not increase while paused."""
        timer = MockTimer()
        timer.start()

        # Simulate 30 seconds passing
        start = timer.state.start_time
        timer.set_mock_time(start + timedelta(seconds=30))

        timer.pause()
        paused_elapsed = timer.elapsed_seconds

        # Simulate more time passing while paused
        timer.set_mock_time(start + timedelta(seconds=60))

        # Elapsed should still be 30
        assert timer.elapsed_seconds == paused_elapsed

    def test_timer_formatted_time(self) -> None:
        """Timer should format time correctly."""
        timer = MockTimer()
        timer.start()

        # Test various times
        start = timer.state.start_time

        # 0 seconds
        timer.set_mock_time(start)
        assert timer.formatted_time == "0:00"

        # 45 seconds
        timer.set_mock_time(start + timedelta(seconds=45))
        assert timer.formatted_time == "0:45"

        # 5 minutes
        timer.set_mock_time(start + timedelta(minutes=5))
        assert timer.formatted_time == "5:00"

        # 1 hour 30 minutes 45 seconds
        timer.set_mock_time(start + timedelta(hours=1, minutes=30, seconds=45))
        assert timer.formatted_time == "1:30:45"

    def test_timer_restore_state(self) -> None:
        """Timer should restore from saved state."""
        # Create a saved state
        start_time = datetime.now() - timedelta(minutes=10)
        state = TimerState(
            is_running=True,
            is_paused=False,
            start_time=start_time,
            pause_time=None,
            accumulated_seconds=0.0,
        )

        timer = Timer()
        timer.restore(state)

        assert timer.is_running
        assert timer.elapsed_seconds >= 600  # At least 10 minutes

    def test_timer_restore_paused_state(self) -> None:
        """Timer should restore paused state correctly."""
        state = TimerState(
            is_running=True,
            is_paused=True,
            start_time=datetime.now() - timedelta(minutes=5),
            pause_time=datetime.now(),
            accumulated_seconds=300.0,  # 5 minutes
        )

        timer = Timer()
        timer.restore(state)

        assert timer.is_paused
        assert timer.elapsed_seconds == 300

    def test_timer_callbacks(self) -> None:
        """Timer should call callbacks on state changes."""
        tick_calls = []
        state_changes = []

        def on_tick(time_str: str) -> None:
            tick_calls.append(time_str)

        def on_state_change(state: TimerState) -> None:
            state_changes.append(state)

        timer = Timer(on_tick=on_tick, on_state_change=on_state_change)

        timer.start()
        assert len(state_changes) == 1
        assert state_changes[-1].is_running

        timer.pause()
        assert len(state_changes) == 2
        assert state_changes[-1].is_paused

        timer.resume()
        assert len(state_changes) == 3
        assert state_changes[-1].is_running

        timer.stop()
        assert len(state_changes) == 4
        assert not state_changes[-1].is_running

    def test_double_start_ignored(self) -> None:
        """Starting an already running timer should be ignored."""
        timer = Timer()
        timer.start()
        original_start = timer.state.start_time

        timer.start()  # Should be ignored
        assert timer.state.start_time == original_start

    def test_pause_when_stopped_ignored(self) -> None:
        """Pausing a stopped timer should be ignored."""
        timer = Timer()
        timer.pause()  # Should be ignored
        assert not timer.is_paused
        assert timer.is_stopped

    def test_resume_when_not_paused_ignored(self) -> None:
        """Resuming when not paused should be ignored."""
        timer = Timer()
        timer.start()
        timer.resume()  # Should be ignored since not paused
        assert timer.is_running
