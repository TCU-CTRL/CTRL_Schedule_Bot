"""Main entry point for the Discord Schedule Reminder Bot."""
import argparse
import logging
from datetime import date

from dotenv import load_dotenv

load_dotenv()

from src.config import Config, ConfigError
from src.date_calculator import DateCalculator
from src.discord_client import DiscordClient, DiscordAPIError
from src.message_formatter import MessageFormatter
from src.reminder_sender import ReminderSender
from src.schedule_parser import ScheduleParser

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def test_connection(config: Config) -> None:
    """Test Discord API connection by fetching messages."""
    logger.info("=== Testing Discord Connection ===")
    client = DiscordClient(config.discord_token)

    logger.info("Fetching messages from schedule channel...")
    messages = client.get_messages(config.schedule_channel_id, limit=50)
    logger.info("Found %d messages:", len(messages))

    parser = ScheduleParser()
    today = date.today()

    for msg in messages:
        content_preview = msg.content[:50] if len(msg.content) > 50 else msg.content
        logger.info("  - [%s] %s", msg.id, repr(content_preview))
        entry = parser.parse_schedule(msg.content, today.year, today.month)
        if entry:
            logger.info("    -> Parsed: %s - %s", entry.activity_date, entry.description)
        else:
            logger.info("    -> Not a valid schedule format")


def test_send(config: Config) -> None:
    """Send a test message to the reminder channel."""
    logger.info("=== Sending Test Message ===")
    client = DiscordClient(config.discord_token)

    test_message = """🧪 テスト送信
これはテストメッセージです。
Botが正常に動作しています！"""

    success = client.post_message(config.reminder_channel_id, test_message)
    if success:
        logger.info("Test message sent successfully!")
    else:
        logger.error("Failed to send test message.")


def test_dry_run(config: Config) -> None:
    """Simulate reminder process without actually sending."""
    logger.info("=== Dry Run (Simulating Reminder) ===")
    client = DiscordClient(config.discord_token)

    today = date.today()
    calculator = DateCalculator()
    parser = ScheduleParser()
    formatter = MessageFormatter()

    logger.info("Today: %s (%s)", today, ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][today.weekday()])

    if calculator.is_reminder_day(today):
        target_date = calculator.get_target_date(today)
        logger.info("Target date: %s", target_date)
    else:
        logger.info("Today is NOT a reminder day. Simulating as Friday...")
        target_date = today + __import__("datetime").timedelta(days=(2 - today.weekday() + 7) % 7)
        if target_date <= today:
            target_date += __import__("datetime").timedelta(days=7)
        logger.info("Simulated target date: %s (next Wednesday)", target_date)

    logger.info("Fetching messages...")
    messages = client.get_messages(config.schedule_channel_id, limit=50)

    found_match = False
    for msg in messages:
        entry = parser.parse_schedule(msg.content, today.year, today.month)
        if entry:
            logger.info("Parsed schedule: %s - %s", entry.activity_date, entry.description)
            if entry.activity_date == target_date:
                found_match = True
                reminder = formatter.format_reminder(entry.activity_date, entry.description)
                logger.info("=== Would send this message ===")
                print(reminder)
                print("=" * 40)

    if not found_match:
        logger.info("No matching schedule found for target date %s", target_date)
        logger.info("To test, post a message like '%d/%d テスト活動' in your schedule channel",
                    target_date.month, target_date.day)


def post_test_schedule(config: Config) -> None:
    """Post a test schedule message to the schedule channel."""
    logger.info("=== Posting Test Schedule ===")
    client = DiscordClient(config.discord_token)

    today = date.today()
    # Create a test schedule for next Wednesday
    import datetime
    days_until_wednesday = (2 - today.weekday() + 7) % 7
    if days_until_wednesday == 0:
        days_until_wednesday = 7
    next_wednesday = today + datetime.timedelta(days=days_until_wednesday)

    test_schedule = f"{next_wednesday.month}/{next_wednesday.day} テスト活動（練習試合）"
    logger.info("Posting schedule: %s", test_schedule)

    success = client.post_message(config.schedule_channel_id, test_schedule)
    if success:
        logger.info("Test schedule posted successfully!")
    else:
        logger.error("Failed to post test schedule.")


def force_send(config: Config, mention_everyone: bool = True) -> None:
    """Force send reminder by scanning all messages in the schedule channel."""
    mode = "with @everyone" if mention_everyone else "without @everyone"
    logger.info("=== Force Send Reminder (Scanning Channel) %s ===", mode)
    client = DiscordClient(config.discord_token)

    today = date.today()
    parser = ScheduleParser()
    formatter = MessageFormatter()

    # Scan all messages in the schedule channel
    logger.info("Scanning schedule channel: %s", config.schedule_channel_id)
    messages = client.get_messages(config.schedule_channel_id, limit=50)
    logger.info("Found %d messages in channel", len(messages))

    # Parse all schedules from all messages
    schedules = []
    for msg in messages:
        # Log raw message content for debugging
        content_preview = msg.content[:100] if len(msg.content) > 100 else msg.content
        logger.info("Message content: %s", repr(content_preview))
        # Try parsing each line of the message
        for line in msg.content.split("\n"):
            entry = parser.parse_schedule(line.strip(), today.year, today.month)
            if entry:
                logger.info("Found schedule: %s - %s", entry.activity_date, entry.description)
                schedules.append(entry)

    if not schedules:
        logger.warning("No valid schedule found in message.")
        return

    # Find the nearest upcoming schedule (today or future)
    upcoming = [s for s in schedules if s.activity_date >= today]
    if upcoming:
        nearest = min(upcoming, key=lambda s: s.activity_date)
        logger.info("Nearest upcoming schedule: %s - %s", nearest.activity_date, nearest.description)
    else:
        # If no upcoming schedules, use the most recent past one
        nearest = max(schedules, key=lambda s: s.activity_date)
        logger.info("No upcoming schedules. Using most recent: %s - %s", nearest.activity_date, nearest.description)

    # Send reminder
    reminder = formatter.format_reminder(
        nearest.activity_date, nearest.description, mention_everyone=mention_everyone
    )
    logger.info("=== Sending reminder %s ===", mode)
    success = client.post_message(config.reminder_channel_id, reminder)
    if success:
        logger.info("Reminder sent successfully!")
    else:
        logger.error("Failed to send reminder.")


def main() -> None:
    """Run the reminder bot."""
    parser = argparse.ArgumentParser(description="Discord Schedule Reminder Bot")
    parser.add_argument(
        "--test",
        choices=["connection", "send", "dry-run", "force", "force-no-mention", "post-schedule"],
        help="Test mode: connection (fetch messages), send (test message), dry-run (simulate), force (send nearest schedule with @everyone), force-no-mention (send without @everyone), post-schedule (post test schedule)"
    )
    args = parser.parse_args()

    try:
        config = Config.load()
        logger.info("Config loaded successfully.")
        # Debug: show last 4 digits of channel IDs for verification
        logger.info("Schedule channel (last 4): ...%s", config.schedule_channel_id[-4:])
        logger.info("Reminder channel (last 4): ...%s", config.reminder_channel_id[-4:])
    except ConfigError as e:
        logger.error("Configuration error: %s", e)
        raise SystemExit(1)

    try:
        if args.test == "connection":
            test_connection(config)
        elif args.test == "send":
            test_send(config)
        elif args.test == "dry-run":
            test_dry_run(config)
        elif args.test == "force":
            force_send(config, mention_everyone=True)
        elif args.test == "force-no-mention":
            force_send(config, mention_everyone=False)
        elif args.test == "post-schedule":
            post_test_schedule(config)
        else:
            # Normal operation
            client = DiscordClient(config.discord_token)
            sender = ReminderSender(
                discord_client=client,
                schedule_channel_id=config.schedule_channel_id,
                reminder_channel_id=config.reminder_channel_id,
            )

            result = sender.run()
            if result:
                logger.info("Reminder process completed successfully.")
            else:
                logger.info("No reminder was sent.")

    except DiscordAPIError as e:
        logger.error("Discord API error: %s", e)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
