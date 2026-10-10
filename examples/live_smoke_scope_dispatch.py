"""Check that a guild command wins over a same-named global command."""

import argparse
import asyncio

import discord
from discord.ext import interaction

from live_smoke_commands import load_local_env, required


async def run(duration: int) -> None:
    load_local_env()
    token = required("DISCORD_TEST_BOT_TOKEN")
    application_id = int(required("DISCORD_TEST_APPLICATION_ID"))
    guild_id = int(required("DISCORD_GUILD_ID"))
    global_scope = interaction.GlobalScope()
    guild_scope = interaction.GuildScope(guild_id)
    bot = interaction.Client(
        intents=discord.Intents.default(), application_id=application_id
    )
    finished = asyncio.Event()
    received = []
    created = []
    name = "codex_smoke_scope"

    async def global_callback(ctx):
        received.append("global")
        await ctx.send("global callback", hidden=True)
        print("global callback received", flush=True)

    async def guild_callback(ctx):
        received.append("guild")
        await ctx.send("guild callback", hidden=True)
        print("guild callback received", flush=True)
        finished.set()

    definitions = (
        interaction.Command(
            global_callback,
            name=name,
            description="Global scope smoke",
            scope=global_scope,
        ),
        interaction.Command(
            guild_callback,
            name=name,
            description="Guild scope smoke",
            scope=guild_scope,
        ),
    )
    for command in definitions:
        bot.add_interaction(command, sync_command=False)

    connect_task = None
    finished_task = None
    try:
        await bot.login(token)
        global_commands = await bot.fetch_commands()
        guild_commands = await bot.fetch_guild_commands(guild_id)
        if name in global_commands[
            interaction.ApplicationCommandType.CHAT_INPUT
        ] or any(
            key.type == interaction.ApplicationCommandType.CHAT_INPUT
            and key.name == name
            for key in guild_commands
        ):
            raise RuntimeError("temporary scope command name already exists")
        for command in definitions:
            data = await bot.register_command(command)
            created.append((command, int(data["id"])))
        print("Run /codex_smoke_scope once in the test guild.", flush=True)
        print(
            "The temporary command is removed after its first successful guild call.",
            flush=True,
        )
        connect_task = asyncio.create_task(bot.connect(reconnect=True))
        finished_task = asyncio.create_task(finished.wait())
        done, _ = await asyncio.wait(
            {connect_task, finished_task},
            timeout=duration,
            return_when=asyncio.FIRST_COMPLETED,
        )
        if connect_task in done:
            await connect_task
        if received != ["guild"]:
            raise AssertionError(f"unexpected scope dispatch: {received}")
        print("guild scope override passed", flush=True)
    finally:
        for task in (connect_task, finished_task):
            if task is not None:
                task.cancel()
        await asyncio.gather(
            *(task for task in (connect_task, finished_task) if task is not None),
            return_exceptions=True,
        )
        for command, command_id in reversed(created):
            await bot.delete_command(command, command_id=command_id)
        if created:
            print(f"deleted {len(created)} temporary scope commands", flush=True)
        await bot.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--duration", type=int, default=300, help="receiver time in seconds"
    )
    args = parser.parse_args()
    if not 30 <= args.duration <= 1800:
        parser.error("duration must be between 30 and 1800 seconds")
    asyncio.run(run(args.duration))
