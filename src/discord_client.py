"""Discord API client for message retrieval and sending."""
from __future__ import annotations

import logging
from dataclasses import dataclass

import requests

logger = logging.getLogger(__name__)

DISCORD_API_BASE = "https://discord.com/api/v10"


class DiscordAPIError(Exception):
    """Raised when Discord API call fails."""

    pass


@dataclass
class DiscordMessage:
    """Represents a Discord message."""

    id: str
    content: str
    timestamp: str


class DiscordClient:
    """Client for Discord REST API communication."""

    def __init__(self, token: str) -> None:
        """
        Initialize Discord client.

        Args:
            token: Discord Bot token for authentication.
        """
        self._token = token
        self._headers = {
            "Authorization": f"Bot {token}",
            "Content-Type": "application/json",
        }

    def get_messages(
        self,
        channel_id: str,
        limit: int = 50,
    ) -> list[DiscordMessage]:
        """
        Retrieve messages from a Discord channel.

        Args:
            channel_id: The ID of the channel to fetch messages from.
            limit: Maximum number of messages to retrieve (default 50).

        Returns:
            List of DiscordMessage objects.

        Raises:
            DiscordAPIError: If API call fails.
        """
        url = f"{DISCORD_API_BASE}/channels/{channel_id}/messages"
        params = {"limit": limit}

        response = requests.get(url, headers=self._headers, params=params)

        if response.status_code != 200:
            logger.error(
                "Failed to get messages: %s - %s",
                response.status_code,
                response.text,
            )
            raise DiscordAPIError(
                f"Failed to get messages: {response.status_code} - {response.text}"
            )

        messages = []
        for msg_data in response.json():
            messages.append(
                DiscordMessage(
                    id=msg_data["id"],
                    content=msg_data["content"],
                    timestamp=msg_data["timestamp"],
                )
            )

        return messages

    def get_message(
        self,
        channel_id: str,
        message_id: str,
    ) -> DiscordMessage:
        """
        Retrieve a specific message from a Discord channel.

        Args:
            channel_id: The ID of the channel containing the message.
            message_id: The ID of the message to fetch.

        Returns:
            DiscordMessage object.

        Raises:
            DiscordAPIError: If API call fails.
        """
        url = f"{DISCORD_API_BASE}/channels/{channel_id}/messages/{message_id}"

        response = requests.get(url, headers=self._headers)

        if response.status_code != 200:
            logger.error(
                "Failed to get message: %s - %s",
                response.status_code,
                response.text,
            )
            raise DiscordAPIError(
                f"Failed to get message: {response.status_code} - {response.text}"
            )

        msg_data = response.json()
        return DiscordMessage(
            id=msg_data["id"],
            content=msg_data["content"],
            timestamp=msg_data["timestamp"],
        )

    def post_message(
        self,
        channel_id: str,
        content: str,
    ) -> bool:
        """
        Send a message to a Discord channel.

        Args:
            channel_id: The ID of the channel to send message to.
            content: The message content to send.

        Returns:
            True if successful, False otherwise.
        """
        url = f"{DISCORD_API_BASE}/channels/{channel_id}/messages"
        payload = {"content": content}

        response = requests.post(url, headers=self._headers, json=payload)

        if response.status_code not in (200, 201):
            logger.error(
                "Failed to send message: %s - %s",
                response.status_code,
                response.text,
            )
            return False

        return True
