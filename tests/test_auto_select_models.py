"""Discord auto-populated selects retain their type and shared fields."""

import pytest

from discord.ext import interaction
from discord.ext.interaction.components import from_payload
from discord.ext.interaction.parser import handle_message_parameter


@pytest.mark.parametrize("model,component_type", [
    (interaction.UserSelect, 5), (interaction.RoleSelect, 6),
    (interaction.MentionableSelect, 7), (interaction.ChannelSelect, 8),
])
def test_auto_select_message_round_trip(model, component_type):
    select = model("pick", placeholder="Choose", min_values=1, max_values=2)
    row = interaction.ActionRow([select])
    params = handle_message_parameter(components=[row])
    assert params.payload["components"][0]["components"][0]["type"] == component_type
    received = from_payload(params.payload["components"])[0].components[0]
    assert isinstance(received, model)
    assert received.to_payload() == select.to_payload()


def test_auto_select_modal_label_serializes_child():
    label = interaction.Label(interaction.UserSelect("user"), label="Choose user")
    assert label.to_all_dict()["component"]["type"] == 5
