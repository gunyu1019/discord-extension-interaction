"""Register three temporary guild commands and verify real Gateway dispatch."""

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
    scope = interaction.GuildScope(guild_id)
    bot = interaction.Client(
        intents=discord.Intents.default(), application_id=application_id
    )
    seen = set()
    finished = asyncio.Event()
    created = []

    async def respond(ctx):
        seen.add(ctx.name)
        await ctx.send(f"{ctx.name} dispatched successfully", hidden=True)
        print(f"received: {ctx.name} type={ctx.application_type}", flush=True)
        if len(seen) == 3:
            finished.set()

    definitions = (
        interaction.Command(
            respond,
            name="codex_smoke_chat",
            description="Temporary smoke command",
            scope=scope,
        ),
        interaction.MemberCommand(respond, name="Codex Smoke User", scope=scope),
        interaction.ContextMenuCommand(
            respond, name="Codex Smoke Message", scope=scope
        ),
    )
    for command in definitions:
        bot.add_interaction(command, sync_command=False)

    connect_task = None
    finished_task = None
    try:
        await bot.login(token)
        existing = await bot.fetch_guild_commands(guild_id)
        existing_keys = {(key.type, key.name) for key in existing}
        if any(
            (command.type, command.name) in existing_keys for command in definitions
        ):
            raise RuntimeError("temporary smoke command name already exists")
        for command in definitions:
            data = await bot.register_command(command)
            created.append((command, int(data["id"])))

        print("Run /codex_smoke_chat in the test guild.", flush=True)
        print("Use Apps > Codex Smoke User on a user.", flush=True)
        print("Use Apps > Codex Smoke Message on a message.", flush=True)
        connect_task = asyncio.create_task(bot.connect(reconnect=True))
        finished_task = asyncio.create_task(finished.wait())
        done, _ = await asyncio.wait(
            {connect_task, finished_task},
            timeout=duration,
            return_when=asyncio.FIRST_COMPLETED,
        )
        if connect_task in done:
            await connect_task
        print(f"received {len(seen)} of 3 command types", flush=True)
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
            print(f"deleted {len(created)} temporary guild commands", flush=True)
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
