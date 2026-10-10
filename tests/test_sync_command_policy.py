"""SyncCommand has explicit immutable operation switches."""

from dataclasses import FrozenInstanceError

import pytest

from discord.ext import interaction


def test_sync_command_defaults_and_immutability():
    policy = interaction.SyncCommand()
    assert (policy.create, policy.edit, policy.delete) == (True, True, True)
    with pytest.raises(FrozenInstanceError):
        policy.delete = False
    assert interaction.SyncCommand(create=False).create is False


def test_sync_command_rejects_non_booleans():
    with pytest.raises(TypeError, match="booleans"):
        interaction.SyncCommand(create=1)
