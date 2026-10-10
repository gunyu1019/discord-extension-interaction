"""New global policy suppresses implicit legacy global synchronization."""

import asyncio
from types import SimpleNamespace

import discord

from discord.ext import interaction


def test_new_policy_suppresses_queued_implicit_legacy_sync(monkeypatch):
    bot = interaction.Client(global_sync_command=True, intents=discord.Intents.none())

    async def callback(context):
        return None

    bot.add_interaction(interaction.Command(callback, name="ping", description="Ping"))
    bot.set_sync_command(
        interaction.GlobalScope(), interaction.SyncCommand(delete=False)
    )
    legacy_calls = []

    async def legacy_sync(**kwargs):
        legacy_calls.append(kwargs)

    async def new_sync(scope, policy):
        return SimpleNamespace(failures=())

    monkeypatch.setattr(bot, "_sync_command", legacy_sync)
    monkeypatch.setattr(bot, "apply_sync_commands", new_sync)
    asyncio.run(bot._sync_command_task())
    assert legacy_calls == []


def test_policy_set_before_registration_skips_implicit_queue(monkeypatch):
    bot = interaction.Client(global_sync_command=True, intents=discord.Intents.none())
    bot.set_sync_command(interaction.GlobalScope(), interaction.SyncCommand())

    async def callback(context):
        return None

    bot.add_interaction(interaction.Command(callback, name="ping", description="Ping"))
    assert bot.get_interaction()[0].name == "ping"
