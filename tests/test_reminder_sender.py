"""Reminder sender tests."""
from datetime import date
from unittest.mock import Mock, patch
import pytest
from src.reminder_sender import ReminderSender
from src.discord_client import DiscordMessage


class TestReminderSender:
    """Test cases for ReminderSender class."""

    def test_run_sends_reminder_on_friday(self) -> None:
        """Send reminder when it's Friday and matching schedule exists."""
        mock_client = Mock()
        mock_client.get_messages.return_value = [
            DiscordMessage(id="1", content="3/25 練習試合", timestamp="2026-03-20T10:00:00Z"),
        ]
        mock_client.post_message.return_value = True

        sender = ReminderSender(
            discord_client=mock_client,
            schedule_channel_id="123",
            reminder_channel_id="456",
        )

        with patch("src.reminder_sender.date") as mock_date:
            mock_date.today.return_value = date(2026, 3, 20)  # Friday
            mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)
            result = sender.run()

        assert result is True
        mock_client.post_message.assert_called_once()
        call_args = mock_client.post_message.call_args
        assert "456" == call_args[0][0]
        assert "練習試合" in call_args[0][1]

    def test_run_sends_reminder_on_monday(self) -> None:
        """Send reminder when it's Monday and matching schedule exists."""
        mock_client = Mock()
        mock_client.get_messages.return_value = [
            DiscordMessage(id="1", content="3/25 定例会", timestamp="2026-03-23T10:00:00Z"),
        ]
        mock_client.post_message.return_value = True

        sender = ReminderSender(
            discord_client=mock_client,
            schedule_channel_id="123",
            reminder_channel_id="456",
        )

        with patch("src.reminder_sender.date") as mock_date:
            mock_date.today.return_value = date(2026, 3, 23)  # Monday
            mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)
            result = sender.run()

        assert result is True
        mock_client.post_message.assert_called_once()

    def test_run_no_reminder_on_wednesday(self) -> None:
        """No reminder sent when it's Wednesday."""
        mock_client = Mock()

        sender = ReminderSender(
            discord_client=mock_client,
            schedule_channel_id="123",
            reminder_channel_id="456",
        )

        with patch("src.reminder_sender.date") as mock_date:
            mock_date.today.return_value = date(2026, 3, 25)  # Wednesday
            result = sender.run()

        assert result is False
        mock_client.get_messages.assert_not_called()
        mock_client.post_message.assert_not_called()

    def test_run_no_matching_schedule(self) -> None:
        """No reminder sent when no matching schedule found."""
        mock_client = Mock()
        mock_client.get_messages.return_value = [
            DiscordMessage(id="1", content="4/1 来週の予定", timestamp="2026-03-20T10:00:00Z"),
        ]

        sender = ReminderSender(
            discord_client=mock_client,
            schedule_channel_id="123",
            reminder_channel_id="456",
        )

        with patch("src.reminder_sender.date") as mock_date:
            mock_date.today.return_value = date(2026, 3, 20)  # Friday
            mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)
            result = sender.run()

        assert result is False
        mock_client.post_message.assert_not_called()

    def test_run_no_valid_messages(self) -> None:
        """No reminder sent when messages don't match schedule format."""
        mock_client = Mock()
        mock_client.get_messages.return_value = [
            DiscordMessage(id="1", content="今日は良い天気です", timestamp="2026-03-20T10:00:00Z"),
        ]

        sender = ReminderSender(
            discord_client=mock_client,
            schedule_channel_id="123",
            reminder_channel_id="456",
        )

        with patch("src.reminder_sender.date") as mock_date:
            mock_date.today.return_value = date(2026, 3, 20)  # Friday
            mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)
            result = sender.run()

        assert result is False
        mock_client.post_message.assert_not_called()
