"""Configured scopes run once per successful readiness cycle."""

import asyncio
from types import SimpleNamespace

from discord.ext import interaction


def test_auto_sync_only_configured_scope_once(monkeypatch, offline_client):
    calls = []
    scope = interaction.GuildScope(42)

    async def apply(selected_scope, policy):
        calls.append((selected_scope, policy))
        return SimpleNamespace(failures=())

    monkeypatch.setattr(offline_client, "apply_sync_commands", apply)
    asyncio.run(offline_client._sync_configured_policies())
    assert calls == []
    offline_client.set_sync_command(scope, interaction.SyncCommand(delete=False))
    asyncio.run(offline_client._sync_configured_policies())
    asyncio.run(offline_client._sync_configured_policies())
    assert len(calls) == 1
    offline_client.set_sync_command(scope, interaction.SyncCommand(create=False))
    asyncio.run(offline_client._sync_configured_policies())
    assert len(calls) == 2


def test_failed_auto_sync_scope_retries(monkeypatch, offline_client):
    scope = interaction.GlobalScope()
    offline_client.set_sync_command(scope, interaction.SyncCommand())
    attempts = []

    async def apply(selected_scope, policy):
        attempts.append(selected_scope)
        return SimpleNamespace(failures=(RuntimeError("failed"),) if len(attempts) == 1 else ())

    monkeypatch.setattr(offline_client, "apply_sync_commands", apply)
    asyncio.run(offline_client._sync_configured_policies())
    asyncio.run(offline_client._sync_configured_policies())
    assert attempts == [scope, scope]
