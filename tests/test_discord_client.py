"""Discord client tests."""
import pytest
from unittest.mock import Mock, patch
from src.discord_client import DiscordClient, DiscordMessage, DiscordAPIError


class TestDiscordClient:
    """Test cases for DiscordClient class."""

    def test_get_messages_success(self) -> None:
        """Successfully retrieve messages from channel."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": "123", "content": "3/20 練習試合", "timestamp": "2026-03-15T10:00:00Z"},
            {"id": "124", "content": "3/27 定例会", "timestamp": "2026-03-16T10:00:00Z"},
        ]

        with patch("requests.get", return_value=mock_response) as mock_get:
            client = DiscordClient("test_token")
            messages = client.get_messages("123456789", limit=50)

            assert len(messages) == 2
            assert messages[0].id == "123"
            assert messages[0].content == "3/20 練習試合"
            assert messages[1].id == "124"

            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert "Authorization" in call_args.kwargs["headers"]
            assert call_args.kwargs["headers"]["Authorization"] == "Bot test_token"

    def test_get_messages_api_error(self) -> None:
        """API error raises DiscordAPIError."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"

        with patch("requests.get", return_value=mock_response):
            client = DiscordClient("invalid_token")

            with pytest.raises(DiscordAPIError) as exc_info:
                client.get_messages("123456789")

            assert "401" in str(exc_info.value)

    def test_post_message_success(self) -> None:
        """Successfully send message to channel."""
        mock_response = Mock()
        mock_response.status_code = 200

        with patch("requests.post", return_value=mock_response) as mock_post:
            client = DiscordClient("test_token")
            result = client.post_message("987654321", "Hello, World!")

            assert result is True
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert call_args.kwargs["json"]["content"] == "Hello, World!"

    def test_post_message_failure(self) -> None:
        """Failed message send returns False."""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.text = "Forbidden"

        with patch("requests.post", return_value=mock_response):
            client = DiscordClient("test_token")
            result = client.post_message("987654321", "Hello!")

            assert result is False
