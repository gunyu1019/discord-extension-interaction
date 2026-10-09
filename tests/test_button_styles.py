"""Button payload fields follow Discord button styles."""

import pytest

from discord.ext import interaction
from discord.ext.interaction.parser import handle_message_parameter


def test_premium_button_serializes_sku_id_as_snowflake():
    button = interaction.Button(style=6, sku_id=123456789)
    payload = button.to_dict()
    assert payload == {"type": 2, "style": 6, "sku_id": "123456789"}
    assert interaction.Button.from_dict(payload).to_dict() == {
        **payload, "disabled": False
    }


def test_valid_button_styles_can_be_sent():
    buttons = [
        interaction.Button(style=1, custom_id="act", label="Act"),
        interaction.Button(style=5, url="https://example.com", label="Visit"),
        interaction.Button(style=6, sku_id=123),
    ]
    assert len(handle_message_parameter(components=[interaction.ActionRow(buttons)]).payload["components"][0]["components"]) == 3


@pytest.mark.parametrize(
    "button",
    [
        interaction.Button(style=1, label="Missing"),
        interaction.Button(style=5, label="Missing"),
        interaction.Button(style=5, url="https://example.com", custom_id="forbidden"),
        interaction.Button(style=6),
        interaction.Button(style=6, sku_id=123, label="Forbidden"),
    ],
)
def test_invalid_button_action_fields_are_rejected_on_send(button):
    with pytest.raises(ValueError, match="Button style"):
        handle_message_parameter(components=[button])
