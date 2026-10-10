"""Public scope values coexist with the legacy guild_id argument."""

import pytest

from discord.ext import interaction


def test_scope_values_and_direct_command_declarations():
    global_command = interaction.SlashCommand(name="ping", description="Ping")
    assert global_command.scope == interaction.GlobalScope()
    scoped = interaction.SlashCommand(
        name="ping", description="Ping", scope=interaction.GuildScope(123),
    )
    assert scoped.guild_id == 123
    assert scoped.scope == interaction.GuildScope(123)
    legacy = interaction.SlashCommand(name="ping", description="Ping", guild_id=123)
    assert legacy.scope == scoped.scope


def test_scope_rejects_invalid_ids_and_conflicts():
    with pytest.raises(ValueError, match="positive"):
        interaction.GuildScope(0)
    with pytest.raises(ValueError, match="different"):
        interaction.SlashCommand(
            name="ping", description="Ping", guild_id=1,
            scope=interaction.GuildScope(2),
        )
