"""Received Components V2 trees are restored as public component models."""

from discord.ext import interaction
from discord.ext.interaction.components import from_payload


def test_received_container_restores_nested_v2_models():
    source = interaction.Container([
        interaction.MediaGallery([
            interaction.MediaGalleryItem(
                interaction.UnfurledMediaItem("https://example.com/a.png")
            )
        ]),
        interaction.Section(
            [interaction.TextDisplay("Caption")],
            interaction.Thumbnail(interaction.UnfurledMediaItem("https://example.com/a.png")),
        ),
    ]).to_payload()
    received = from_payload([source])[0]
    assert isinstance(received, interaction.Container)
    assert isinstance(received.components[0], interaction.MediaGallery)
    assert isinstance(received.components[1].accessory, interaction.Thumbnail)
    assert received.to_payload() == source
