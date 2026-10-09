"""Auto-select interactions expose raw IDs and resolved Discord objects."""

import discord

from discord.ext import interaction
from discord.ext.interaction import interaction as interaction_module


def test_user_select_values_resolve_users(monkeypatch, offline_client, user_payload):
    monkeypatch.setattr(interaction_module, "Message", lambda **kwargs: kwargs)
    user_id = user_payload["id"]
    payload = {
        "id": "40", "application_id": "20", "type": 3, "token": "tk",
        "version": 1, "user": user_payload, "channel_id": "30",
        "data": {
            "component_type": 5, "custom_id": "users", "values": [user_id, "999"],
            "resolved": {"users": {user_id: user_payload}},
        },
        "message": {},
    }
    context = interaction.ComponentsContext(payload, offline_client)
    assert context.values == [user_id, "999"]
    assert isinstance(context.resolved_values[0], discord.User)
    assert context.resolved_values[1] == "999"


def test_string_select_values_remain_strings(monkeypatch, offline_client, user_payload):
    monkeypatch.setattr(interaction_module, "Message", lambda **kwargs: kwargs)
    payload = {
        "id": "40", "application_id": "20", "type": 3, "token": "tk",
        "version": 1, "user": user_payload, "channel_id": "30",
        "data": {"component_type": 3, "custom_id": "strings", "values": ["red"]},
        "message": {},
    }
    context = interaction.ComponentsContext(payload, offline_client)
    assert context.resolved_values == ["red"]
