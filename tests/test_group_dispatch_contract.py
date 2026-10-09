"""Application command dispatch must traverse Discord's nested option payload."""

import asyncio
from types import SimpleNamespace

import discord

from discord.ext import interaction


def test_group_subcommand_executes_its_callback():
    client = interaction.Client(intents=discord.Intents.none())
    received = []

    @interaction.command(name="manage", description="Manage members")
    async def manage(ctx):
        pass

    @manage.subcommand_group(name="members")
    async def members(ctx):
        pass

    @members.subcommand(name="add")
    async def add(ctx, name: str):
        received.append(name)

    client.add_interaction(manage)
    ctx = SimpleNamespace(
        application_type=interaction.ApplicationCommandType.CHAT_INPUT.value,
        name="manage",
        options={
            "subcommand_group": SimpleNamespace(
                name="members",
                options={
                    "subcommand": SimpleNamespace(name="add", options={"name": "Ada"})
                },
            )
        },
        function=None,
        parents=None,
    )

    asyncio.run(client.process_interaction(ctx))

    assert received == ["Ada"]
    assert ctx.function is add


def test_direct_subcommand_still_executes_its_callback():
    client = interaction.Client(intents=discord.Intents.none())
    received = []

    @interaction.command(name="manage", description="Manage members")
    async def manage(ctx):
        pass

    @manage.subcommand(name="add")
    async def add(ctx, name: str):
        received.append(name)

    client.add_interaction(manage)
    ctx = SimpleNamespace(
        application_type=interaction.ApplicationCommandType.CHAT_INPUT.value,
        name="manage",
        options={"subcommand": SimpleNamespace(name="add", options={"name": "Ada"})},
        function=None,
        parents=None,
    )

    asyncio.run(client.process_interaction(ctx))

    assert received == ["Ada"]
    assert ctx.function is add
