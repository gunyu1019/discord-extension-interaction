"""New component models activate the IS_COMPONENTS_V2 message flag."""

import discord
import pytest

from discord.ext import interaction
from discord.ext.interaction.component_models import UnknownComponent
from discord.ext.interaction.parser import handle_interaction_message_parameter, handle_message_parameter


def test_v2_message_sets_flag_and_preserves_existing_flags():
    existing = discord.MessageFlags(suppress_notifications=True)
    params = handle_message_parameter(
        components=[interaction.TextDisplay("Hello")], flags=existing
    )
    assert params.payload["flags"] & 32768
    assert params.payload["flags"] & existing.value
    assert existing.value == 4096
    assert params.payload["components"] == [{"type": 10, "content": "Hello"}]


def test_v2_interaction_callback_sets_flag():
    params = handle_interaction_message_parameter(
        interaction_type=4, components=[interaction.TextDisplay("Hello")]
    )
    assert params.payload["data"]["flags"] & 32768


def test_legacy_message_does_not_add_v2_flag():
    button = interaction.Button(style=1, label="Go", custom_id="go")
    params = handle_message_parameter(components=[button])
    assert params.payload.get("flags", 0) & 32768 == 0


@pytest.mark.parametrize(
    "keyword",
    [
        {"content": "old content"},
        {"embed": discord.Embed(title="old embed")},
        {"embeds": [discord.Embed(title="old embed")]},
        {"poll": object()},
        {"stickers": [123]},
    ],
)
def test_v2_rejects_disabled_legacy_message_fields(keyword):
    with pytest.raises(ValueError, match="Components V2"):
        handle_message_parameter(components=[interaction.TextDisplay("New")], **keyword)


def test_v2_interaction_callback_rejects_content():
    with pytest.raises(ValueError, match="content"):
        handle_interaction_message_parameter(
            interaction_type=4,
            content="old content",
            components=[interaction.TextDisplay("New")],
        )


def test_v2_component_limit_counts_nested_components():
    children = [interaction.TextDisplay(f"item {index}") for index in range(39)]
    accepted = handle_message_parameter(components=[interaction.Container(children)])
    assert len(accepted.payload["components"][0]["components"]) == 39
    with pytest.raises(ValueError, match="at most 40"):
        handle_message_parameter(
            components=[interaction.Container(children + [interaction.TextDisplay("extra")])]
        )


def test_v2_rejects_thumbnail_at_top_level():
    with pytest.raises(ValueError, match="V2 position"):
        handle_message_parameter(components=[
            interaction.Thumbnail(interaction.UnfurledMediaItem("https://example.com/a.png"))
        ])


def test_v2_rejects_duplicate_component_ids():
    with pytest.raises(ValueError, match="duplicate component id"):
        handle_message_parameter(components=[
            interaction.TextDisplay("One", id=7),
            interaction.TextDisplay("Two", id=7),
        ])


def test_v2_rejects_duplicate_custom_ids_across_nested_sections():
    button = UnknownComponent({"type": 2, "style": 1, "label": "Go", "custom_id": "go"})
    sections = [interaction.Section([interaction.TextDisplay(str(i))], button) for i in range(2)]
    with pytest.raises(ValueError, match="duplicate component custom_id"):
        handle_message_parameter(components=[interaction.Container(sections)])
