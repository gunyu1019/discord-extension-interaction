"""Activity commands serialize PRIMARY_ENTRY_POINT and handler metadata."""

import pytest

from discord.ext import interaction
from discord.ext.interaction.models.commands import from_payload
from discord.ext.interaction.implementation.command_comparison import same_command_declaration


def test_activity_command_round_trip_and_comparison():
    command = interaction.ActivityCommand(
        "launch", "Open the Activity", handler=interaction.ActivityHandler.APP_HANDLER,
    )
    payload = command.to_register_dict()
    assert payload["type"] == 4
    assert payload["handler"] == 1
    remote = from_payload({**payload, "id": "50", "application_id": "20", "version": "3"})
    assert isinstance(remote, interaction.ActivityCommand)
    assert same_command_declaration(command, remote)


def test_activity_command_rejects_guild_scope_and_unknown_handler():
    with pytest.raises(ValueError, match="guild"):
        interaction.ActivityCommand("launch", "Open", guild_id=123)
    with pytest.raises(ValueError, match="handler"):
        interaction.ActivityCommand("launch", "Open", handler=9)
