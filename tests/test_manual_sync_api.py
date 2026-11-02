"""Manual sync previews changes before applying an explicit policy."""

import asyncio

import pytest

from discord.ext import interaction
from discord.ext.interaction import client as client_module
from discord.ext.interaction.sync_executor import SyncOutcome
from discord.ext.interaction.sync_planner import SyncOperation


def test_manual_preview_and_apply_require_policy(monkeypatch, offline_client):
    scope = interaction.GlobalScope()
    local = interaction.Command(lambda ctx: None, name="ping", description="Ping")
    offline_client.add_interaction(local, sync_command=False)

    async def global_commands(*args):
        return []

    async def app_id():
        return 20

    monkeypatch.setattr(client_module, "get_global_commands_with_localizations", global_commands)
    monkeypatch.setattr(offline_client, "_application_id", app_id)
    plan = asyncio.run(offline_client.plan_sync_commands(scope))
    assert plan.items[0].operation is SyncOperation.CREATE
    with pytest.raises(ValueError, match="policy is required"):
        asyncio.run(offline_client.apply_sync_commands(scope))

    calls = []

    class Transport:
        def __init__(self, http, application_id):
            pass

        async def create(self, scope, command):
            calls.append(command.name)

    monkeypatch.setattr(client_module, "CommandSyncAPI", Transport)
    result = asyncio.run(offline_client.apply_sync_commands(
        scope, interaction.SyncCommand(edit=False, delete=False),
    ))
    assert calls == ["ping"]
    assert result.items[0].outcome is SyncOutcome.APPLIED
