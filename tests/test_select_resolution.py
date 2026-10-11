"""Auto-select interactions expose raw IDs and resolved Discord objects."""

import discord
from types import SimpleNamespace

from discord.ext import interaction
from discord.ext.interaction.implementation import interaction as interaction_module
from discord.ext.interaction.implementation.resolved_selects import resolve_select_values


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


def test_role_mentionable_and_channel_select_resolve_entities(offline_client, user_payload):
    context = SimpleNamespace(
        _resolved={
            "users": {user_payload["id"]: user_payload},
            "roles": {"600": {"id": "600", "name": "admin"}},
            "channels": {"700": {"id": "700", "guild_id": "300", "type": 0, "name": "general"}},
        },
        _state=offline_client._connection,
        guild_id="300", guild=None, client=offline_client,
    )
    assert isinstance(resolve_select_values(context, 6, ["600"])[0], discord.Role)
    assert isinstance(resolve_select_values(context, 7, [user_payload["id"]])[0], discord.User)
    assert isinstance(resolve_select_values(context, 8, ["700"])[0], discord.TextChannel)
