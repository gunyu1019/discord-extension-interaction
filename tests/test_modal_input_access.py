"""Modal input lookup retains the legacy flat components list."""

import discord
import pytest

from discord.ext import interaction


def test_modal_input_lookup_and_resolved_select(offline_client, user_payload):
    user_id = user_payload["id"]
    payload = {
        "id": "40", "application_id": "20", "type": 5, "token": "tk",
        "version": 1, "user": user_payload, "channel_id": "30",
        "data": {
            "custom_id": "survey",
            "resolved": {"users": {user_id: user_payload}},
            "components": [
                {"type": 18, "component": {
                    "type": 5, "custom_id": "users", "values": [user_id],
                }},
                {"type": 18, "component": {
                    "type": 23, "custom_id": "accept", "value": False,
                }},
            ],
        },
    }
    context = interaction.ModalSubmitContext(payload, offline_client)
    assert len(context.components) == 2
    assert context.get_component("users") is context.components[0]
    assert context.get_component("accept").value is False
    assert context.get_component("missing") is None
    assert isinstance(context.get_resolved_values("users")[0], discord.User)
    with pytest.raises(KeyError):
        context.get_resolved_values("missing")
    with pytest.raises(TypeError, match="Select Menu"):
        context.get_resolved_values("accept")
