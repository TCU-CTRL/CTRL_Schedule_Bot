"""Date calculator tests."""
from datetime import date
import pytest
from src.date_calculator import DateCalculator


class TestDateCalculator:
    """Test cases for DateCalculator class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.calculator = DateCalculator()

    def test_get_target_date_friday(self) -> None:
        """Friday returns next Wednesday (5 days later)."""
        friday = date(2026, 3, 20)  # Friday
        result = self.calculator.get_target_date(friday)

        assert result == date(2026, 3, 25)  # Next Wednesday

    def test_get_target_date_monday(self) -> None:
        """Monday returns this Wednesday (2 days later)."""
        monday = date(2026, 3, 23)  # Monday
        result = self.calculator.get_target_date(monday)

        assert result == date(2026, 3, 25)  # This Wednesday

    def test_get_target_date_tuesday(self) -> None:
        """Tuesday returns None (not a reminder day)."""
        tuesday = date(2026, 3, 24)
        result = self.calculator.get_target_date(tuesday)

        assert result is None

    def test_get_target_date_wednesday(self) -> None:
        """Wednesday returns None (not a reminder day)."""
        wednesday = date(2026, 3, 25)
        result = self.calculator.get_target_date(wednesday)

        assert result is None

    def test_get_target_date_thursday(self) -> None:
        """Thursday returns None (not a reminder day)."""
        thursday = date(2026, 3, 26)
        result = self.calculator.get_target_date(thursday)

        assert result is None

    def test_get_target_date_saturday(self) -> None:
        """Saturday returns None (not a reminder day)."""
        saturday = date(2026, 3, 21)
        result = self.calculator.get_target_date(saturday)

        assert result is None

    def test_get_target_date_sunday(self) -> None:
        """Sunday returns None (not a reminder day)."""
        sunday = date(2026, 3, 22)
        result = self.calculator.get_target_date(sunday)

        assert result is None

    def test_is_reminder_day_friday(self) -> None:
        """Friday is a reminder day."""
        friday = date(2026, 3, 20)
        assert self.calculator.is_reminder_day(friday) is True

    def test_is_reminder_day_monday(self) -> None:
        """Monday is a reminder day."""
        monday = date(2026, 3, 23)
        assert self.calculator.is_reminder_day(monday) is True

    def test_is_reminder_day_wednesday(self) -> None:
        """Wednesday is not a reminder day."""
        wednesday = date(2026, 3, 25)
        assert self.calculator.is_reminder_day(wednesday) is False

    def test_get_target_date_friday_month_boundary(self) -> None:
        """Friday at month boundary calculates correctly."""
        friday = date(2026, 3, 27)  # Friday
        result = self.calculator.get_target_date(friday)

        assert result == date(2026, 4, 1)  # Next Wednesday in April
