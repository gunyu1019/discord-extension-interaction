"""Remote command cache separates global and guild name collisions."""

import asyncio

from discord.ext import interaction
from discord.ext.interaction.implementation import client as client_module


def test_remote_command_lists_keep_scopes_separate(monkeypatch, offline_client):
    async def app_id():
        return 20

    async def global_commands(*args):
        return [{"id": "1", "type": 1, "name": "ping", "description": "Global"}]

    async def guild_commands(*args):
        return [{"id": "2", "type": 1, "name": "ping", "description": "Guild"}]

    monkeypatch.setattr(offline_client, "_application_id", app_id)
    monkeypatch.setattr(client_module, "get_global_commands_with_localizations", global_commands)
    monkeypatch.setattr(client_module, "get_guild_commands_with_localizations", guild_commands)
    asyncio.run(offline_client.fetch_commands())
    guild = asyncio.run(offline_client.fetch_guild_commands(42))
    global_scope = interaction.GlobalScope()
    guild_scope = interaction.GuildScope(42)
    registry = offline_client._remote_command_registry
    assert registry.get(global_scope, interaction.ApplicationCommandType.CHAT_INPUT, "ping").id == "1"
    assert registry.get(guild_scope, interaction.ApplicationCommandType.CHAT_INPUT, "ping").id == "2"
    assert next(iter(guild)).scope == guild_scope
