"""Command identity includes scope, type and name."""

from discord.ext import interaction
from discord.ext.interaction.sync import CommandRegistry


def test_registry_keeps_same_name_across_scopes_and_types():
    registry = CommandRegistry()
    global_chat = interaction.SlashCommand(name="open", description="Open")
    guild_chat = interaction.SlashCommand(
        name="open", description="Open here", scope=interaction.GuildScope(42),
    )
    global_user = interaction.UserCommand(name="open")
    for command in (global_chat, guild_chat, global_user):
        registry.add(command)
    assert registry.get(interaction.GuildScope(42), global_chat.type, "open") is guild_chat
    assert registry.get(interaction.GuildScope(99), global_chat.type, "open", fallback_global=True) is global_chat
    assert registry.get(interaction.GlobalScope(), global_user.type, "open") is global_user
    assert len(registry.all()) == 3


def test_registry_removal_affects_only_one_scope():
    registry = CommandRegistry()
    global_command = interaction.SlashCommand(name="open", description="Open")
    guild_command = interaction.SlashCommand(
        name="open", description="Open", scope=interaction.GuildScope(42),
    )
    registry.add(global_command)
    registry.add(guild_command)
    registry.remove(guild_command)
    assert registry.get(interaction.GuildScope(42), global_command.type, "open") is None
    assert registry.get(interaction.GlobalScope(), global_command.type, "open") is global_command
