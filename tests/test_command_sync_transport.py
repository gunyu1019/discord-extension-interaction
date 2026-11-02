"""Sync transport selects matching global or guild Discord REST methods."""

import asyncio

from discord.ext import interaction
from discord.ext.interaction.http import CommandSyncAPI


class HTTP:
    def __init__(self):
        self.calls = []

    async def upsert_global_command(self, application_id, payload):
        self.calls.append(("global-create", application_id, payload))

    async def upsert_guild_command(self, application_id, guild_id, payload):
        self.calls.append(("guild-create", application_id, guild_id, payload))

    async def edit_global_command(self, application_id, command_id, payload):
        self.calls.append(("global-edit", application_id, command_id, payload))

    async def edit_guild_command(self, application_id, guild_id, command_id, payload):
        self.calls.append(("guild-edit", application_id, guild_id, command_id, payload))

    async def delete_global_command(self, application_id, command_id):
        self.calls.append(("global-delete", application_id, command_id))

    async def delete_guild_command(self, application_id, guild_id, command_id):
        self.calls.append(("guild-delete", application_id, guild_id, command_id))


def test_command_sync_transport_uses_scope_specific_endpoints():
    http = HTTP()
    api = CommandSyncAPI(http, 20)
    global_scope = interaction.GlobalScope()
    guild_scope = interaction.GuildScope(42)
    global_command = interaction.SlashCommand(name="ping", description="Ping")
    guild_command = interaction.SlashCommand(name="ping", description="Ping", scope=guild_scope)
    remote = type("Remote", (), {"id": "9"})()

    async def run():
        await api.create(global_scope, global_command)
        await api.create(guild_scope, guild_command)
        await api.edit(global_scope, global_command, remote)
        await api.edit(guild_scope, guild_command, remote)
        await api.delete(global_scope, remote)
        await api.delete(guild_scope, remote)

    asyncio.run(run())
    assert [call[0] for call in http.calls] == [
        "global-create", "guild-create", "global-edit", "guild-edit",
        "global-delete", "guild-delete",
    ]
    assert http.calls[-1] == ("guild-delete", 20, 42, 9)
