"""Sync comparison uses declared Discord fields, not server metadata."""

from discord.ext.interaction.application.command_comparison import (
    same_command_declaration,
)
from discord.ext.interaction.commands import SlashCommand, from_payload


def _remote(**overrides):
    return from_payload({
        "id": "100", "application_id": "200", "version": "300",
        "type": 1, "name": "hello", "description": "say hello",
        "name_localizations": {"ko": "안녕"},
        "nsfw": True,
        **overrides,
    })


def _local():
    return SlashCommand(
        name="hello", description="say hello",
        name_localizations={"ko": "안녕"}, nsfw=True,
    )


def test_comparison_ignores_server_assigned_id_and_version():
    local = _local()
    remote = _remote()
    assert local.id != remote.id
    assert local.version != remote.version
    assert same_command_declaration(local, remote)


def test_comparison_detects_localization_and_nsfw_changes():
    local = _local()
    assert not same_command_declaration(local, _remote(name_localizations={"ko": "반가워"}))
    assert not same_command_declaration(local, _remote(nsfw=False))


def test_comparison_keeps_guild_scope_separate():
    local = _local()
    remote = _remote(guild_id="123")
    assert not same_command_declaration(local, remote)


def test_comparison_accepts_same_guild_id_across_int_and_snowflake_string():
    local = _local()
    local.guild_id = 123
    assert same_command_declaration(local, _remote(guild_id="123"))
