"""Configuration module for loading environment variables."""
from __future__ import annotations

import os
from dataclasses import dataclass


class ConfigError(Exception):
    """Raised when required configuration is missing."""

    pass


@dataclass(frozen=True)
class Config:
    """Application configuration loaded from environment variables."""

    discord_token: str
    schedule_channel_id: str
    reminder_channel_id: str

    @classmethod
    def load(cls) -> Config:
        """
        Load configuration from environment variables.

        Returns:
            Config instance with all required values.

        Raises:
            ConfigError: If any required environment variable is missing.
        """
        discord_token = os.environ.get("DISCORD_TOKEN")
        if not discord_token:
            raise ConfigError("DISCORD_TOKEN environment variable is not set")

        schedule_channel_id = os.environ.get("SCHEDULE_CHANNEL_ID")
        if not schedule_channel_id:
            raise ConfigError("SCHEDULE_CHANNEL_ID environment variable is not set")

        reminder_channel_id = os.environ.get("REMINDER_CHANNEL_ID")
        if not reminder_channel_id:
            raise ConfigError("REMINDER_CHANNEL_ID environment variable is not set")

        return cls(
            discord_token=discord_token,
            schedule_channel_id=schedule_channel_id,
            reminder_channel_id=reminder_channel_id,
        )
