"""Reminder sender orchestration module."""
from __future__ import annotations

import logging
from datetime import date

from src.date_calculator import DateCalculator
from src.discord_client import DiscordClient
from src.message_formatter import MessageFormatter
from src.schedule_parser import ScheduleParser

logger = logging.getLogger(__name__)


class ReminderSender:
    """Orchestrates the reminder sending process."""

    def __init__(
        self,
        discord_client: DiscordClient,
        schedule_channel_id: str,
        reminder_channel_id: str,
    ) -> None:
        """
        Initialize the reminder sender.

        Args:
            discord_client: Client for Discord API communication.
            schedule_channel_id: ID of the channel containing schedules.
            reminder_channel_id: ID of the channel to send reminders to.
        """
        self._client = discord_client
        self._schedule_channel_id = schedule_channel_id
        self._reminder_channel_id = reminder_channel_id
        self._date_calculator = DateCalculator()
        self._schedule_parser = ScheduleParser()
        self._message_formatter = MessageFormatter()

    def run(self) -> bool:
        """
        Execute the reminder process.

        Returns:
            True if reminder was sent successfully, False otherwise.
        """
        today = date.today()

        if not self._date_calculator.is_reminder_day(today):
            logger.info("Today is not a reminder day. Skipping.")
            return False

        target_date = self._date_calculator.get_target_date(today)
        if target_date is None:
            logger.info("Could not determine target date.")
            return False

        logger.info("Looking for schedule on %s", target_date)

        messages = self._client.get_messages(self._schedule_channel_id)
        current_year = today.year
        current_month = today.month

        for message in messages:
            entries = self._schedule_parser.parse_message(
                message.content,
                current_year,
                current_month,
            )

            for entry in entries:
                if entry.activity_date == target_date:
                    logger.info(
                        "Found matching schedule: %s",
                        entry.description,
                    )

                    reminder_message = (
                        self._message_formatter.format_reminder(
                            entry.activity_date,
                            entry.description,
                        )
                    )

                    success = self._client.post_message(
                        self._reminder_channel_id,
                        reminder_message,
                    )

                    if success:
                        logger.info("Reminder sent successfully.")
                        return True
                    else:
                        logger.error("Failed to send reminder.")
                        return False

        logger.info("No matching schedule found for %s", target_date)
        return False
