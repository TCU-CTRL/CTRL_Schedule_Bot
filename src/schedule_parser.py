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
BULLET_DAY_PATTERN = re.compile(r"[・･](\d{1,2})日\s*$")


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

    def has_day_only_entries(self, message_content: str) -> bool:
        """Check if a message contains day-only (・DD日) entries."""
        for line in message_content.split("\n"):
            if BULLET_DAY_PATTERN.match(line.strip()):
                return True
        return False

    def parse_message(
        self,
        message_content: str,
        reference_year: int,
        current_month: int,
        skip_day_only: bool = False,
    ) -> list[ScheduleEntry]:
        """
        Parse a full message and return all schedule entries.

        Supports single-line formats (M/D, M月D日：) and
        multi-line bullet format (・DD日 with description
        on the next line, using current_month as the month).

        Args:
            message_content: The full message text.
            reference_year: The base year for date interpretation.
            current_month: Current month for day-only entries
                           and year boundary handling.

        Returns:
            List of parsed ScheduleEntry objects.
        """
        entries: list[ScheduleEntry] = []
        lines = message_content.split("\n")
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            # Try single-line formats first
            entry = self.parse_schedule(
                line, reference_year, current_month,
            )
            if entry:
                entries.append(entry)
                i += 1
                continue

            # Try ・DD日 bullet format (skip if requested)
            if skip_day_only:
                i += 1
                continue
            bullet_match = BULLET_DAY_PATTERN.match(line)
            if bullet_match:
                day = int(bullet_match.group(1))
                # Find next non-empty line as description
                i += 1
                while i < len(lines) and not lines[i].strip():
                    i += 1
                if i < len(lines):
                    desc = lines[i].strip()
                    try:
                        activity_date = date(
                            reference_year,
                            current_month,
                            day,
                        )
                        entries.append(ScheduleEntry(
                            activity_date=activity_date,
                            description=desc,
                            original_text=line,
                        ))
                    except ValueError:
                        logger.warning(
                            "Invalid day %d for month %d",
                            day, current_month,
                        )
                i += 1
                continue

            i += 1

        return entries
