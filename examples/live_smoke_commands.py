"""Read-only preflight or isolated command CRUD against a Discord test app.

Run from the repository root. Credentials are read from the ignored .env file.
The --crud option creates uniquely named commands and deletes only their IDs.
"""

import argparse
import asyncio
import os
from pathlib import Path
from uuid import uuid4

import discord
from discord.ext import interaction


def load_local_env() -> None:
    path = Path(__file__).resolve().parents[1] / ".env"
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if "=" not in line or line.lstrip().startswith("#"):
            continue
        name, value = line.split("=", 1)
        name = name.strip()
        if name.startswith("DISCORD_TEST_") or name == "DISCORD_GUILD_ID":
            os.environ.setdefault(name, value.strip().strip('"').strip("'"))


def required(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise ValueError(f"missing {name}")
    return value


async def inspect_scope(bot, scope):
    if isinstance(scope, interaction.GlobalScope):
        commands = await bot.fetch_commands()
        return [item for by_type in commands.values() for item in by_type.values()]
    commands = await bot.fetch_guild_commands(scope.guild_id)
    return list(commands.values())


async def exercise_scope(bot, scope) -> None:
    suffix = uuid4().hex[:8]
    prefix = f"codex_smoke_{suffix}"
    definitions = (
        interaction.SlashCommand(
            name=f"{prefix}_chat", description="Smoke test", scope=scope
        ),
        interaction.UserCommand(name=f"{prefix}_user", scope=scope),
        interaction.ContextMenu(name=f"{prefix}_message", scope=scope),
    )
    existing = {(item.type, item.name) for item in await inspect_scope(bot, scope)}
    if any((item.type, item.name) in existing for item in definitions):
        raise RuntimeError("generated command name already exists")

    created = []
    try:
        for command in definitions:
            data = await bot.register_command(command)
            command_id = int(data["id"])
            created.append((command, command_id))
            fetched = await bot.fetch_command(command_id, scope=scope)
            if fetched.name != command.name or fetched.type != command.type:
                raise AssertionError("created command did not round-trip")

        listing = await inspect_scope(bot, scope)
        listed = {(item.type, item.name) for item in listing}
        if not all((item.type, item.name) in listed for item in definitions):
            raise AssertionError("created command missing from scope listing")

        chat, chat_id = created[0]
        chat.description = "Smoke test edited"
        await bot.edit_command(chat, command_id=chat_id)
        fetched = await bot.fetch_command(chat_id, scope=scope)
        if fetched.description != chat.description:
            raise AssertionError("edited command did not round-trip")
        print(f"{scope}: create/list/fetch/edit passed for {len(created)} commands")
    finally:
        for command, command_id in reversed(created):
            await bot.delete_command(command, command_id=command_id)
        if created:
            remaining = {
                (item.type, item.name) for item in await inspect_scope(bot, scope)
            }
            if any((item.type, item.name) in remaining for item, _ in created):
                raise AssertionError("smoke command remained after deletion")
            print(f"{scope}: delete passed for {len(created)} commands")


async def run(crud: bool) -> None:
    load_local_env()
    token = required("DISCORD_TEST_BOT_TOKEN")
    application_id = int(required("DISCORD_TEST_APPLICATION_ID"))
    guild_id = int(
        os.environ.get("DISCORD_TEST_GUILD_ID") or required("DISCORD_GUILD_ID")
    )
    if application_id <= 0 or guild_id <= 0:
        raise ValueError("application and guild IDs must be positive")
    bot = interaction.Client(
        intents=discord.Intents.none(), application_id=application_id
    )
    try:
        await bot.login(token)
        global_scope = interaction.GlobalScope()
        guild_scope = interaction.GuildScope(guild_id)
        for scope in (global_scope, guild_scope):
            commands = await inspect_scope(bot, scope)
            print(f"{scope}: read {len(commands)} commands")
        if crud:
            for scope in (guild_scope, global_scope):
                await exercise_scope(bot, scope)
    finally:
        await bot.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--crud", action="store_true", help="create, edit, and delete test commands"
    )
    args = parser.parse_args()
    try:
        asyncio.run(run(args.crud))
    except Exception as error:
        print(
            f"smoke failed: {type(error).__name__} (status={getattr(error, 'status', '-')})"
        )
        raise SystemExit(1) from None
