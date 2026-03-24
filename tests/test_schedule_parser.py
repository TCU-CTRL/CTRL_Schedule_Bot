"""Schedule parser tests."""
from datetime import date
import pytest
from src.schedule_parser import ScheduleParser


class TestScheduleParser:
    """Test cases for ScheduleParser class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.parser = ScheduleParser()

    def test_parse_valid_schedule(self) -> None:
        """Parse valid schedule format."""
        result = self.parser.parse_schedule("3/20 練習試合", 2026)

        assert result is not None
        assert result.activity_date == date(2026, 3, 20)
        assert result.description == "練習試合"
        assert result.original_text == "3/20 練習試合"

    def test_parse_single_digit_date(self) -> None:
        """Parse single digit month and day."""
        result = self.parser.parse_schedule("1/5 新年会", 2026)

        assert result is not None
        assert result.activity_date == date(2026, 1, 5)
        assert result.description == "新年会"

    def test_parse_double_digit_date(self) -> None:
        """Parse double digit month and day."""
        result = self.parser.parse_schedule("12/25 クリスマス会", 2026)

        assert result is not None
        assert result.activity_date == date(2026, 12, 25)
        assert result.description == "クリスマス会"

    def test_parse_with_extra_spaces(self) -> None:
        """Parse with multiple spaces between date and description."""
        result = self.parser.parse_schedule("3/20   練習試合", 2026)

        assert result is not None
        assert result.description == "練習試合"

    def test_parse_invalid_format_no_date(self) -> None:
        """Return None for message without date."""
        result = self.parser.parse_schedule("今日は練習です", 2026)

        assert result is None

    def test_parse_invalid_format_no_description(self) -> None:
        """Return None for message with only date."""
        result = self.parser.parse_schedule("3/20", 2026)

        assert result is None

    def test_parse_invalid_month(self) -> None:
        """Return None for invalid month."""
        result = self.parser.parse_schedule("13/20 練習", 2026)

        assert result is None

    def test_parse_invalid_day(self) -> None:
        """Return None for invalid day."""
        result = self.parser.parse_schedule("2/30 練習", 2026)

        assert result is None

    def test_parse_year_boundary_december_to_january(self) -> None:
        """Handle year boundary when parsing January date in December."""
        result = self.parser.parse_schedule("1/5 新年会", 2026, current_month=12)

        assert result is not None
        assert result.activity_date == date(2027, 1, 5)

    def test_parse_same_year_in_early_months(self) -> None:
        """Keep same year when parsing in early months."""
        result = self.parser.parse_schedule("3/20 練習", 2026, current_month=2)

        assert result is not None
        assert result.activity_date == date(2026, 3, 20)
