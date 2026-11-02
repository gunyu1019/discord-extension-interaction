"""V2 trees and legacy rows share message payloads without losing structure."""

from discord.ext import interaction
from discord.ext.interaction.components import from_payload
from discord.ext.interaction.parser import handle_message_parameter


def test_nested_v2_tree_survives_send_and_receive():
    thumbnail = interaction.Thumbnail(
        interaction.UnfurledMediaItem("https://example.com/thumb.png"),
        description="Preview",
    )
    section = interaction.Section([interaction.TextDisplay("# News")], thumbnail)
    gallery = interaction.MediaGallery([
        interaction.MediaGalleryItem(
            interaction.UnfurledMediaItem("https://example.com/large.png")
        )
    ])
    container = interaction.Container(
        [section, interaction.Separator(), gallery], accent_color=0x123456
    )
    params = handle_message_parameter(components=[container])
    assert params.payload["flags"] & 32768
    received = from_payload(params.payload["components"])
    assert received[0].to_payload() == container.to_payload()


def test_legacy_action_row_and_v2_text_can_share_payload():
    row = interaction.ActionRow([
        interaction.Button(style=1, label="Open", custom_id="open")
    ])
    text = interaction.TextDisplay("Choose an option")
    params = handle_message_parameter(components=[text, row])
    assert params.payload["flags"] & 32768
    assert [item["type"] for item in params.payload["components"]] == [10, 1]
    restored = from_payload(params.payload["components"])
    assert isinstance(restored[0], interaction.TextDisplay)
    assert isinstance(restored[1], interaction.ActionRow)
