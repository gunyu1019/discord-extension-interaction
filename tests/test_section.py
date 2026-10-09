"""Section retains its child and accessory component payloads."""

import pytest

from discord.ext import interaction


def test_section_round_trip():
    accessory = interaction.Thumbnail(interaction.UnfurledMediaItem("https://example.com/a.png"))
    section = interaction.Section([interaction.TextDisplay("Hello")], accessory, id=2)
    payload = section.to_payload()
    restored = interaction.Section.from_payload(payload)
    assert restored.to_payload() == payload
    assert isinstance(restored.components[0], interaction.TextDisplay)


@pytest.mark.parametrize("count", [0, 4])
def test_section_requires_one_to_three_children(count):
    accessory = interaction.Thumbnail(interaction.UnfurledMediaItem("https://example.com/a.png"))
    with pytest.raises(ValueError, match="1 to 3"):
        interaction.Section([interaction.TextDisplay("x")] * count, accessory)
