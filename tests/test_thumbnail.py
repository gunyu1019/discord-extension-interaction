"""Thumbnail and unfurled media item preserve Discord media data."""

import pytest

from discord.ext import interaction


def test_thumbnail_section_round_trip():
    media = interaction.UnfurledMediaItem("https://example.com/a.png")
    thumbnail = interaction.Thumbnail(media, description="An image", id=3)
    section = interaction.Section([interaction.TextDisplay("Hello")], thumbnail)
    restored = interaction.Section.from_payload(section.to_payload())
    assert restored.to_payload() == section.to_payload()
    assert isinstance(restored.accessory, interaction.Thumbnail)


def test_unfurled_media_item_preserves_response_fields():
    payload = {"url": "https://example.com/a.png", "width": 100, "height": 50}
    assert interaction.UnfurledMediaItem.from_payload(payload).to_payload() == payload


def test_thumbnail_rejects_long_description():
    with pytest.raises(ValueError, match="description"):
        interaction.Thumbnail(interaction.UnfurledMediaItem("https://example.com/a.png"), description="x" * 1025)
