"""Schedule message parser for extracting date and activity information."""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import date
from typing import Optional

logger = logging.getLogger(__name__)

SCHEDULE_PATTERN = re.compile(r"(\d{1,2})/(\d{1,2})\s+(.+)")
JAPANESE_DATE_PATTERN = re.compile(r"(\d{1,2})月(\d{1,2})日[：:](.+)")


@dataclass
class ScheduleEntry:
    """Represents a parsed schedule entry."""

    activity_date: date
    description: str
    original_text: str


class ScheduleParser:
    """Parser for extracting schedule information from messages."""

    def parse_schedule(
        self,
        message_content: str,
        reference_year: int,
        current_month: Optional[int] = None,
    ) -> Optional[ScheduleEntry]:
        """
        Parse a message to extract schedule information.

        Args:
            message_content: The message text to parse.
            reference_year: The base year for date interpretation.
            current_month: Current month for year boundary handling (optional).

        Returns:
            ScheduleEntry if parsing succeeds, None otherwise.
        """
        text = message_content.strip()
        match = SCHEDULE_PATTERN.match(text) or JAPANESE_DATE_PATTERN.match(text)

        if not match:
            logger.debug("Message does not match schedule pattern: %s", message_content)
            return None

        month_str, day_str, description = match.groups()

        try:
            month = int(month_str)
            day = int(day_str)

            if month < 1 or month > 12:
                logger.warning("Invalid month value: %d", month)
                return None

            year = reference_year
            if current_month is not None and current_month >= 11 and month <= 2:
                year = reference_year + 1

            activity_date = date(year, month, day)

        except ValueError as e:
            logger.warning("Invalid date in message '%s': %s", message_content, e)
            return None

        return ScheduleEntry(
            activity_date=activity_date,
            description=description.strip(),
            original_text=message_content.strip(),
        )
