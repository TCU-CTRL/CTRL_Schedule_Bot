"""Config module tests."""
import os
import pytest
from src.config import Config, ConfigError


class TestConfig:
    """Test cases for Config class."""

    def test_load_config_with_all_env_vars(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """All required environment variables are set."""
        monkeypatch.setenv("DISCORD_TOKEN", "test_token_123")
        monkeypatch.setenv("SCHEDULE_CHANNEL_ID", "123456789")
        monkeypatch.setenv("REMINDER_CHANNEL_ID", "987654321")

        config = Config.load()

        assert config.discord_token == "test_token_123"
        assert config.schedule_channel_id == "123456789"
        assert config.reminder_channel_id == "987654321"

    def test_load_config_missing_discord_token(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Missing DISCORD_TOKEN raises ConfigError."""
        monkeypatch.delenv("DISCORD_TOKEN", raising=False)
        monkeypatch.setenv("SCHEDULE_CHANNEL_ID", "123456789")
        monkeypatch.setenv("REMINDER_CHANNEL_ID", "987654321")

        with pytest.raises(ConfigError) as exc_info:
            Config.load()

        assert "DISCORD_TOKEN" in str(exc_info.value)

    def test_load_config_missing_schedule_channel_id(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Missing SCHEDULE_CHANNEL_ID raises ConfigError."""
        monkeypatch.setenv("DISCORD_TOKEN", "test_token_123")
        monkeypatch.delenv("SCHEDULE_CHANNEL_ID", raising=False)
        monkeypatch.setenv("REMINDER_CHANNEL_ID", "987654321")

        with pytest.raises(ConfigError) as exc_info:
            Config.load()

        assert "SCHEDULE_CHANNEL_ID" in str(exc_info.value)

    def test_load_config_missing_reminder_channel_id(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Missing REMINDER_CHANNEL_ID raises ConfigError."""
        monkeypatch.setenv("DISCORD_TOKEN", "test_token_123")
        monkeypatch.setenv("SCHEDULE_CHANNEL_ID", "123456789")
        monkeypatch.delenv("REMINDER_CHANNEL_ID", raising=False)

        with pytest.raises(ConfigError) as exc_info:
            Config.load()

        assert "REMINDER_CHANNEL_ID" in str(exc_info.value)
