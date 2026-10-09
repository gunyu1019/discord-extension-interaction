"""Text Display follows the Discord Component Object fields."""

import pytest

from discord.ext import interaction


def test_text_display_round_trip_with_id():
    payload = {"type": 10, "id": 7, "content": "# Heading\nHello"}
    display = interaction.TextDisplay.from_payload(payload)
    assert display.type == 10
    assert display.to_payload() == payload


def test_text_display_requires_nonempty_content():
    with pytest.raises(ValueError, match="content"):
        interaction.TextDisplay("")
