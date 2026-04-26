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

    def test_run_multiline_message(self) -> None:
        """Send reminder when matching schedule is in a multi-line message."""
        multiline = "5月6日：オンライン\n5月13日：自己紹介\n5月20日：進捗発表会\n5月27日：未定"
        mock_client = Mock()
        mock_client.get_messages.return_value = [
            DiscordMessage(id="1", content=multiline, timestamp="2026-05-18T10:00:00Z"),
        ]
        mock_client.post_message.return_value = True

        sender = ReminderSender(
            discord_client=mock_client,
            schedule_channel_id="123",
            reminder_channel_id="456",
        )

        with patch("src.reminder_sender.date") as mock_date:
            mock_date.today.return_value = date(2026, 5, 18)  # Monday
            mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)
            result = sender.run()

        assert result is True
        mock_client.post_message.assert_called_once()
        call_args = mock_client.post_message.call_args
        assert "進捗発表会" in call_args[0][1]

    def test_run_bullet_day_format(self) -> None:
        """Send reminder when schedule uses ・DD日 format."""
        message = "・20日\n活動紹介\n\n・27日\n講習会"
        mock_client = Mock()
        mock_client.get_messages.return_value = [
            DiscordMessage(
                id="1", content=message,
                timestamp="2026-05-18T10:00:00Z",
            ),
        ]
        mock_client.post_message.return_value = True

        sender = ReminderSender(
            discord_client=mock_client,
            schedule_channel_id="123",
            reminder_channel_id="456",
        )

        with patch("src.reminder_sender.date") as mock_date:
            mock_date.today.return_value = date(2026, 5, 18)  # Monday
            mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
            result = sender.run()

        assert result is True
        call_args = mock_client.post_message.call_args
        assert "活動紹介" in call_args[0][1]

    def test_run_skips_old_day_only_messages(self) -> None:
        """Only the newest day-only message is used; older ones are skipped."""
        # Messages come newest first from Discord API
        new_msg = "・20日\n進捗発表会\n\n・27日\n未定"  # May (current month)
        old_msg = "・15日\n旧活動\n\n・22日\n旧講習会"  # Also day-only, but older
        mock_client = Mock()
        mock_client.get_messages.return_value = [
            DiscordMessage(id="2", content=new_msg, timestamp="2026-05-01T10:00:00Z"),
            DiscordMessage(id="1", content=old_msg, timestamp="2026-04-01T10:00:00Z"),
        ]
        mock_client.post_message.return_value = True

        sender = ReminderSender(
            discord_client=mock_client,
            schedule_channel_id="123",
            reminder_channel_id="456",
        )

        # Monday May 18 -> target is Wednesday May 20
        with patch("src.reminder_sender.date") as mock_date:
            mock_date.today.return_value = date(2026, 5, 18)
            mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
            result = sender.run()

        assert result is True
        call_args = mock_client.post_message.call_args
        assert "進捗発表会" in call_args[0][1]

    def test_run_old_day_only_not_matched(self) -> None:
        """Old day-only message should not produce a match."""
        # Only the old message has day 20, but it should be skipped
        new_msg = "・27日\n新活動"
        old_msg = "・20日\n旧活動"
        mock_client = Mock()
        mock_client.get_messages.return_value = [
            DiscordMessage(id="2", content=new_msg, timestamp="2026-05-10T10:00:00Z"),
            DiscordMessage(id="1", content=old_msg, timestamp="2026-04-01T10:00:00Z"),
        ]

        sender = ReminderSender(
            discord_client=mock_client,
            schedule_channel_id="123",
            reminder_channel_id="456",
        )

        # Monday May 18 -> target is Wednesday May 20
        # Only old_msg has 20日, but it should be skipped
        with patch("src.reminder_sender.date") as mock_date:
            mock_date.today.return_value = date(2026, 5, 18)
            mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
            result = sender.run()

        assert result is False
        mock_client.post_message.assert_not_called()

    def test_run_explicit_month_messages_always_processed(self) -> None:
        """Messages with explicit month (M/D, M月D日) are always processed."""
        day_only_msg = "・20日\n活動紹介"
        explicit_msg = "4/1 進捗報告会"
        mock_client = Mock()
        mock_client.get_messages.return_value = [
            DiscordMessage(id="2", content=day_only_msg, timestamp="2026-05-01T10:00:00Z"),
            DiscordMessage(id="1", content=explicit_msg, timestamp="2026-03-31T10:00:00Z"),
        ]
        mock_client.post_message.return_value = True

        sender = ReminderSender(
            discord_client=mock_client,
            schedule_channel_id="123",
            reminder_channel_id="456",
        )

        # Friday March 27 -> target is Wednesday April 1
        with patch("src.reminder_sender.date") as mock_date:
            mock_date.today.return_value = date(2026, 3, 27)
            mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
            result = sender.run()

        assert result is True
        call_args = mock_client.post_message.call_args
        assert "進捗報告会" in call_args[0][1]

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
