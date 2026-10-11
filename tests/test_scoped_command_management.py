"""Existing direct command management methods honor GuildScope."""

import asyncio

from discord.ext import interaction


def test_guild_command_create_edit_delete_use_guild_routes(monkeypatch, offline_client):
    scope = interaction.GuildScope(42)
    command = interaction.SlashCommand(name="ping", description="Ping", scope=scope)
    calls = []

    async def app_id():
        return 20

    async def fetch(guild_id):
        calls.append(("fetch", guild_id))
        offline_client._remote_command_registry.replace_scope(scope, [])

    async def create(http, app_id, guild_id, payload):
        calls.append(("create", app_id, guild_id, payload["name"]))

    async def edit(http, app_id, guild_id, command_id, payload):
        calls.append(("edit", app_id, guild_id, command_id))

    async def delete(http, app_id, guild_id, command_id):
        calls.append(("delete", app_id, guild_id, command_id))

    from discord.ext.interaction.implementation import client as client_module
    monkeypatch.setattr(offline_client, "_application_id", app_id)
    monkeypatch.setattr(offline_client, "fetch_guild_commands", fetch)
    monkeypatch.setattr(client_module, "create_guild_command", create)
    monkeypatch.setattr(client_module, "edit_guild_command", edit)
    monkeypatch.setattr(client_module, "delete_guild_command", delete)

    async def run():
        await offline_client.register_command(command)
        await offline_client.edit_command(command, command_id=7)
        await offline_client.delete_command(command, command_id=7)

    asyncio.run(run())
    assert calls == [
        ("fetch", 42), ("create", 20, 42, "ping"),
        ("edit", 20, 42, 7), ("delete", 20, 42, 7),
    ]


def test_fetch_guild_command_by_id_preserves_scope(monkeypatch, offline_client):
    from discord.ext.interaction.implementation import client as client_module

    async def app_id():
        return 20

    async def get_command(http, app_id, guild_id, command_id):
        assert (app_id, guild_id, command_id) == (20, 42, 7)
        return {"id": "7", "type": 1, "name": "ping", "description": "Ping"}

    monkeypatch.setattr(offline_client, "_application_id", app_id)
    monkeypatch.setattr(client_module, "get_guild_command", get_command)
    command = asyncio.run(offline_client.fetch_command(
        7, use_cached=True, scope=interaction.GuildScope(42),
    ))
    assert command.scope == interaction.GuildScope(42)
