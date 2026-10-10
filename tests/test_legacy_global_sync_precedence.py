"""Scoped policies take precedence over legacy command synchronization."""

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


def test_policy_suppresses_explicit_registration_queued_before_ready(monkeypatch):
    bot = interaction.Client(intents=discord.Intents.none())

    async def callback(context):
        return None

    command = interaction.Command(callback, name="ping", description="Ping")
    bot.add_interaction(command, sync_command=True)
    bot.set_sync_command(interaction.GlobalScope(), interaction.SyncCommand())
    legacy_calls = []

    async def legacy_sync(**kwargs):
        legacy_calls.append(kwargs)

    async def new_sync(scope, policy):
        return SimpleNamespace(failures=())

    monkeypatch.setattr(bot, "_sync_command", legacy_sync)
    monkeypatch.setattr(bot, "apply_sync_commands", new_sync)
    asyncio.run(bot._sync_command_task())
    assert legacy_calls == []


def test_policy_suppresses_explicit_registration_and_deletion(monkeypatch):
    bot = interaction.Client(intents=discord.Intents.none())
    scope = interaction.GuildScope(42)
    bot.set_sync_command(scope, interaction.SyncCommand())

    async def callback(context):
        return None

    command = interaction.Command(
        callback, name="ping", description="Ping", scope=scope
    )
    bot.add_interaction(command, sync_command=True)
    bot.delete_interaction(command, sync_command=True)

    async def unexpected(**kwargs):
        raise AssertionError("legacy synchronization must not run")

    async def new_sync(selected_scope, policy):
        return SimpleNamespace(failures=())

    monkeypatch.setattr(bot, "_sync_command", unexpected)
    monkeypatch.setattr(bot, "_sync_command_popping", unexpected)
    monkeypatch.setattr(bot, "apply_sync_commands", new_sync)
    asyncio.run(bot._sync_command_task())


def test_policy_suppresses_already_scheduled_legacy_coroutines(monkeypatch):
    bot = interaction.Client(intents=discord.Intents.none())
    command = interaction.SlashCommand(name="ping", description="Ping")
    bot.set_sync_command(interaction.GlobalScope(), interaction.SyncCommand())

    async def ready():
        return None

    async def unexpected():
        raise AssertionError("remote command fetch must not run")

    monkeypatch.setattr(bot, "wait_until_ready", ready)
    monkeypatch.setattr(bot, "_fetch_command_cached", unexpected)
    asyncio.run(bot._sync_command(command))
    asyncio.run(bot._sync_command_popping(command))
