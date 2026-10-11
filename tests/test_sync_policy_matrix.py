"""All eight create/edit/delete combinations gate only their own operation."""

import asyncio
from itertools import product

import pytest

from discord.ext import interaction
from discord.ext.interaction.implementation.command_registry import CommandRegistry
from discord.ext.interaction.implementation.sync_executor import SyncOutcome, apply_sync_plan
from discord.ext.interaction.implementation.sync_planner import plan_sync


@pytest.mark.parametrize("create,edit,delete", list(product((False, True), repeat=3)))
def test_sync_policy_matrix(create, edit, delete):
    scope = interaction.GuildScope(42)
    local, remote = CommandRegistry(), CommandRegistry()
    local.add(interaction.SlashCommand(name="create", description="New", scope=scope))
    local.add(interaction.SlashCommand(name="edit", description="New", scope=scope))
    remote.add(interaction.SlashCommand(name="edit", description="Old", scope=scope))
    remote.add(interaction.SlashCommand(name="delete", description="Old", scope=scope))
    calls = []

    class Transport:
        async def create(self, scope, command):
            calls.append("create")

        async def edit(self, scope, command, existing):
            calls.append("edit")

        async def delete(self, scope, existing):
            calls.append("delete")

    result = asyncio.run(apply_sync_plan(
        plan_sync(scope, local, remote),
        interaction.SyncCommand(create=create, edit=edit, delete=delete),
        Transport(),
    ))
    assert set(calls) == {
        name for name, allowed in (("create", create), ("edit", edit), ("delete", delete))
        if allowed
    }
    assert len([item for item in result.items if item.outcome is SyncOutcome.APPLIED]) == len(calls)
