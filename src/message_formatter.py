"""Message formatter for creating reminder messages."""
from __future__ import annotations

from datetime import date

WEEKDAY_NAMES = ["月", "火", "水", "木", "金", "土", "日"]


class MessageFormatter:
    """Formatter for creating reminder messages."""

    def format_reminder(
        self,
        activity_date: date,
        description: str,
        mention_everyone: bool = True,
    ) -> str:
        """
        Format a reminder message for the activity.

        Args:
            activity_date: The date of the activity.
            description: The activity description.
            mention_everyone: Whether to include @everyone mention.

        Returns:
            Formatted reminder message string.
        """
        weekday_name = WEEKDAY_NAMES[activity_date.weekday()]
        date_str = f"{activity_date.month}/{activity_date.day}（{weekday_name}）"

        mention = "@everyone\n" if mention_everyone else ""

        message = f"""{mention}📅 今週の活動予定
日付: {date_str}
内容: {description}

準備をお願いします！"""

        return message
