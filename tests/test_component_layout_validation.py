"""Message ActionRows reject invalid Discord component arrangements."""

import pytest

from discord.ext import interaction
from discord.ext.interaction.parser import handle_message_parameter


def _button(index):
    return interaction.Button(style=1, label=str(index), custom_id=f"button-{index}")


def test_message_action_row_accepts_buttons_or_one_select():
    buttons = interaction.ActionRow([_button(1), _button(2)])
    select = interaction.ActionRow([
        interaction.Selection(
            custom_id="pick", options=[interaction.SelectOption("A", "a")]
        )
    ])

    assert handle_message_parameter(content="hello", components=[buttons]).payload[
        "components"
    ][0]["type"] == 1
    assert handle_message_parameter(content="hello", components=[select]).payload[
        "components"
    ][0]["components"][0]["type"] == 3


@pytest.mark.parametrize(
    "children",
    [
        [],
        [_button(index) for index in range(6)],
        [_button(1), interaction.Selection("pick", [])],
        [interaction.ActionRow([_button(1)])],
    ],
)
def test_message_action_row_rejects_invalid_children(children):
    with pytest.raises(ValueError, match="ActionRow"):
        handle_message_parameter(
            content="hello", components=[interaction.ActionRow(children)]
        )
