"""Automatic synchronization is disabled outside explicitly configured scopes."""

from discord.ext import interaction


def test_client_stores_global_and_guild_policies_independently(offline_client):
    global_scope = interaction.GlobalScope()
    guild_scope = interaction.GuildScope(42)
    assert offline_client.get_sync_command(global_scope) is None
    assert offline_client.get_sync_command(guild_scope) is None
    offline_client.set_sync_command(global_scope, interaction.SyncCommand(delete=False))
    offline_client.set_sync_command(guild_scope, interaction.SyncCommand(create=False))
    assert offline_client.get_sync_command(global_scope).delete is False
    assert offline_client.get_sync_command(guild_scope).create is False
    assert offline_client.get_sync_command(interaction.GuildScope(43)) is None
    offline_client.remove_sync_command(guild_scope)
    assert offline_client.get_sync_command(guild_scope) is None
    assert offline_client.get_sync_command(global_scope).delete is False
