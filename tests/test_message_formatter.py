"""Message formatter tests."""
from datetime import date
import pytest
from src.message_formatter import MessageFormatter


class TestMessageFormatter:
    """Test cases for MessageFormatter class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.formatter = MessageFormatter()

    def test_format_reminder_wednesday(self) -> None:
        """Format reminder for Wednesday activity."""
        activity_date = date(2026, 3, 25)  # Wednesday
        description = "練習試合"

        result = self.formatter.format_reminder(activity_date, description)

        assert "📅 今週の活動予定" in result
        assert "3/25（水）" in result
        assert "練習試合" in result
        assert "準備をお願いします" in result

    def test_format_reminder_includes_all_parts(self) -> None:
        """Format includes @everyone, header, date, content, and footer."""
        activity_date = date(2026, 4, 1)  # Wednesday
        description = "定例会"

        result = self.formatter.format_reminder(activity_date, description)

        lines = result.strip().split("\n")
        assert len(lines) >= 5
        assert "@everyone" in lines[0]
        assert "📅" in lines[1]
        assert "日付" in result
        assert "内容" in result

    def test_format_reminder_without_mention(self) -> None:
        """Format without @everyone mention."""
        activity_date = date(2026, 4, 1)  # Wednesday
        description = "定例会"

        result = self.formatter.format_reminder(
            activity_date, description, mention_everyone=False
        )

        assert "@everyone" not in result
        assert "📅 今週の活動予定" in result

    def test_format_reminder_different_months(self) -> None:
        """Format correctly for different months."""
        activity_date = date(2026, 12, 2)  # Wednesday
        description = "忘年会"

        result = self.formatter.format_reminder(activity_date, description)

        assert "12/2（水）" in result
        assert "忘年会" in result

    def test_format_reminder_single_digit_day(self) -> None:
        """Format correctly for single digit day."""
        activity_date = date(2026, 1, 7)  # Wednesday
        description = "新年会"

        result = self.formatter.format_reminder(activity_date, description)

        assert "1/7（水）" in result
