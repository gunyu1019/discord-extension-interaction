"""Container carries nested layout content and RGB styling."""

import pytest

from discord.ext import interaction


def test_container_round_trip_with_nested_section():
    accessory = interaction.Thumbnail(interaction.UnfurledMediaItem("https://example.com/a.png"))
    section = interaction.Section([interaction.TextDisplay("Hello")], accessory)
    container = interaction.Container(
        [section, interaction.Separator(spacing=2), interaction.TextDisplay("Bye")],
        accent_color=0xABCDEF,
        spoiler=True,
        id=5,
    )
    payload = container.to_payload()
    restored = interaction.Container.from_payload(payload)
    assert restored.to_payload() == payload
    assert isinstance(restored.components[0], interaction.Section)


@pytest.mark.parametrize("color", [-1, 0x1000000, True])
def test_container_rejects_invalid_accent_color(color):
    with pytest.raises(ValueError, match="accent_color"):
        interaction.Container([interaction.TextDisplay("ok")], accent_color=color)
