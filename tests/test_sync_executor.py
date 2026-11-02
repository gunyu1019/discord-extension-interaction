"""Sync executor respects policy switches and retains partial failures."""

import asyncio

from discord.ext import interaction
from discord.ext.interaction.sync import CommandRegistry
from discord.ext.interaction.sync import plan_sync
from discord.ext.interaction.sync import SyncOutcome, apply_sync_plan


def test_sync_executor_skips_deletes_and_reports_partial_failure():
    local, remote = CommandRegistry(), CommandRegistry()
    local.add(interaction.SlashCommand(name="create", description="New"))
    local.add(interaction.SlashCommand(name="edit", description="New"))
    remote.add(interaction.SlashCommand(name="edit", description="Old"))
    remote.add(interaction.SlashCommand(name="delete", description="Old"))
    plan = plan_sync(interaction.GlobalScope(), local, remote)
    calls = []

    class Transport:
        async def create(self, scope, command):
            calls.append(("create", command.name))
            return {"id": "1"}

        async def edit(self, scope, command, existing):
            calls.append(("edit", command.name))
            raise RuntimeError("Discord rejected edit")

        async def delete(self, scope, existing):
            calls.append(("delete", existing.name))

    result = asyncio.run(apply_sync_plan(
        plan, interaction.SyncCommand(delete=False), Transport(),
    ))
    assert calls == [("create", "create"), ("edit", "edit")]
    assert [item.outcome for item in result.items] == [
        SyncOutcome.APPLIED, SyncOutcome.SKIPPED, SyncOutcome.FAILED,
    ]
    assert str(result.failures[0].error) == "Discord rejected edit"
