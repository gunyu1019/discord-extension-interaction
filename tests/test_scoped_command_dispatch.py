"""Guild commands with the same name override global commands in that guild."""

import asyncio
from types import SimpleNamespace

from discord.ext import interaction


def test_client_registers_and_dispatches_by_scope(offline_client):
    seen = []

    async def global_callback(context):
        seen.append("global")

    async def guild_callback(context):
        seen.append("guild")

    global_command = interaction.Command(
        global_callback, name="ping", description="Ping",
    )
    guild_command = interaction.Command(
        guild_callback, name="ping", description="Ping guild",
        scope=interaction.GuildScope(42),
    )
    offline_client.add_interaction(global_command, sync_command=False)
    offline_client.add_interaction(guild_command, sync_command=False)
    assert offline_client.get_interaction() == [global_command, guild_command]

    for guild_id in ("42", "99", None):
        context = SimpleNamespace(
            application_type=1, name="ping", guild_id=guild_id,
            function=None, parents=None, options={},
        )
        asyncio.run(offline_client.process_interaction(context))
    assert seen == ["guild", "global", "global"]

    offline_client.delete_interaction(guild_command, sync_command=False)
    assert offline_client.get_interaction() == [global_command]
