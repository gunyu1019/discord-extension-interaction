"""Temporary Gateway receiver for hands-on component and modal smoke tests."""

import argparse
import asyncio
from io import BytesIO

import discord
from discord.ext import interaction

from live_smoke_commands import load_local_env, required
from live_smoke_message import message_components


def input_modal():
    return [
        interaction.Label(interaction.TextInput("smoke_note", 1), label="Note"),
        interaction.Label(interaction.FileUpload("smoke_file"), label="Upload a file"),
        interaction.Label(
            interaction.RadioGroup(
                "smoke_radio",
                [
                    interaction.RadioGroupOption("a", "Choice A"),
                    interaction.RadioGroupOption("b", "Choice B"),
                ],
            ),
            label="Radio choice",
        ),
        interaction.Label(
            interaction.CheckboxGroup(
                "smoke_checks", [interaction.CheckboxGroupOption("a", "Check A")]
            ),
            label="Checkbox group",
        ),
        interaction.Label(interaction.Checkbox("smoke_accept"), label="Accept"),
    ]


def select_modal():
    return [
        interaction.Label(
            interaction.Selection(
                "smoke_string",
                [
                    interaction.SelectOption("Choice A", "a"),
                    interaction.SelectOption("Choice B", "b"),
                ],
            ),
            label="String choice",
        )
    ]


async def run(duration: int) -> None:
    load_local_env()
    token = required("DISCORD_TEST_BOT_TOKEN")
    application_id = int(required("DISCORD_TEST_APPLICATION_ID"))
    guild_id = int(required("DISCORD_GUILD_ID"))
    channel_id = int(required("DISCORD_TEST_CHANNEL_ID"))
    bot = interaction.Client(
        intents=discord.Intents.default(), application_id=application_id
    )
    state = {"message": None, "seen": set()}

    async def on_ready():
        if state["message"] is not None:
            return
        channel = await bot.fetch_channel(channel_id)
        if channel.guild.id != guild_id:
            raise ValueError("test channel is not in test guild")
        file = discord.File(
            BytesIO(b"Discord Components V2 live smoke test\n"), filename="smoke.txt"
        )
        state["message"] = await interaction.MessageTransferable(
            bot._connection, channel
        ).send(components=message_components(bot.user.display_avatar.url), file=file)
        print(
            f"Open https://discord.com/channels/{guild_id}/{channel_id}/{state['message'].id}",
            flush=True,
        )
        print("Click both buttons and the four select menus.", flush=True)

    async def on_components(ctx):
        custom_id = ctx.custom_id
        if not custom_id or not custom_id.startswith("codex_smoke_"):
            return
        state["seen"].add(custom_id)
        if custom_id == "codex_smoke_modal":
            await ctx.modal("codex_smoke_inputs", "Input smoke test", input_modal())
            print("input modal opened", flush=True)
        elif custom_id == "codex_smoke_select_modal":
            await ctx.modal(
                "codex_smoke_select_inputs", "Select smoke test", select_modal()
            )
            print("select modal opened", flush=True)
        else:
            await ctx.send(
                f"{custom_id}: values={len(ctx.values)}, resolved={len(ctx.resolved_values)}",
                hidden=True,
            )
            print(
                f"{custom_id}: values={len(ctx.values)}, resolved={len(ctx.resolved_values)}",
                flush=True,
            )

    async def on_modal(ctx):
        if ctx.custom_id == "codex_smoke_inputs":
            note = ctx.get_component("smoke_note")
            files = ctx.get_component("smoke_file")
            radio = ctx.get_component("smoke_radio")
            checks = ctx.get_component("smoke_checks")
            accept = ctx.get_component("smoke_accept")
            uploaded = ctx.file_uploads.get("smoke_file", [])
            if not (
                note
                and note.value
                and files
                and files.values
                and len(uploaded) == len(files.values)
                and radio
                and radio.value in ("a", "b")
                and checks
                and checks.values
                and accept
                and type(accept.value) is bool
            ):
                raise AssertionError("modal submitted values were not fully resolved")
            await ctx.send(
                "All five modal values were parsed and the file resolved.", hidden=True
            )
            state["seen"].add(ctx.custom_id)
            print(
                "five modal values parsed; uploaded files resolved:",
                len(uploaded),
                flush=True,
            )
        elif ctx.custom_id == "codex_smoke_select_inputs":
            selected = ctx.get_component("smoke_string")
            if selected is None or not selected.values:
                raise AssertionError("String Select value missing")
            await ctx.send("String Select value parsed.", hidden=True)
            state["seen"].add(ctx.custom_id)
            print("String Select value parsed", flush=True)

    bot.add_listener(on_ready, "on_ready")
    bot.add_listener(on_components, "on_components")
    bot.add_listener(on_modal, "on_modal")
    try:
        await asyncio.wait_for(bot.start(token), timeout=duration)
    except asyncio.TimeoutError:
        print("Gateway smoke window ended", flush=True)
    finally:
        print("events received:", ", ".join(sorted(state["seen"])), flush=True)
        if state["message"] is not None:
            await bot.http.delete_message(channel_id, state["message"].id)
            print("smoke message deleted", flush=True)
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
