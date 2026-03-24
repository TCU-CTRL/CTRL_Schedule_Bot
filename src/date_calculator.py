"""Date calculator for determining reminder target dates."""
from __future__ import annotations

from datetime import date, timedelta
from typing import Optional


class DateCalculator:
    """Calculator for determining reminder dates and target activity dates."""

    MONDAY = 0
    FRIDAY = 4
    WEDNESDAY = 2

    def get_target_date(self, today: date) -> Optional[date]:
        """
        Calculate the target activity date for reminder.

        Args:
            today: The current date (execution date).

        Returns:
            - If Friday: Next Wednesday (5 days later)
            - If Monday: This Wednesday (2 days later)
            - Otherwise: None (not a reminder day)
        """
        weekday = today.weekday()

        if weekday == self.FRIDAY:
            return today + timedelta(days=5)
        elif weekday == self.MONDAY:
            return today + timedelta(days=2)
        else:
            return None

    def is_reminder_day(self, today: date) -> bool:
        """
        Check if today is a reminder day (Friday or Monday).

        Args:
            today: The date to check.

        Returns:
            True if Friday or Monday, False otherwise.
        """
        weekday = today.weekday()
        return weekday in (self.FRIDAY, self.MONDAY)
