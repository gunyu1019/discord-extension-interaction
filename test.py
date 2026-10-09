"""Manual smoke test against a real bot.

    setx DISCORD_TOKEN "<bot token>"   (Windows, new shell)   OR
    $env:DISCORD_TOKEN = "<bot token>" (PowerShell, this shell)
    python test.py

Invite the bot with the ``applications.commands`` scope, then in any guild run:

  /ping            -> ctx.send
  /secret          -> ephemeral (hidden=True)
  /slow            -> defer -> edit deferred -> followup
  /file            -> attachment (forces defer + multipart)
  /buttons         -> wait_for_component + detect_component + components_cancelled
  /form            -> modal (Action Row) ; submit -> on_modal reads ctx.components
  /form2           -> modal (Label, type 18)      ; submit -> on_modal
  /fruit name:<..> -> autocomplete
  /whoami user:@x  -> option resolution (member)

Watch the console: command sync on startup, dispatched events, and any
on_interaction_command_error traceback.
"""
import io
import logging
import os
import traceback

import discord

from discord.ext import interaction

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s | %(name)s | %(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("smoke")

TOKEN = os.environ.get("DISCORD_TOKEN")
if not TOKEN:
    raise SystemExit("Set the DISCORD_TOKEN environment variable to a bot token.")

intents = discord.Intents.default()
client = interaction.Client(global_sync_command=True, intents=intents)


@client.listen()
async def on_ready():
    try:
        import zstandard  # noqa: F401

        compression = "zstd-stream (zstandard installed)"
    except ModuleNotFoundError:
        compression = "zlib-stream"
    log.info("logged in as %s (id %s)", client.user, client.user.id)
    log.info("discord.py %s | gateway compression: %s", discord.__version__, compression)
    log.info("registered: %s", [c.name for c in client.get_interaction()])


@client.listen()
async def on_interaction_command_error(ctx, error):
    log.error("command error in /%s:\n%s", getattr(ctx, "name", "?"),
              "".join(traceback.format_exception(type(error), error, error.__traceback__)))


# ---------------------------------------------------------------- send
@interaction.command(name="ping", description="basic ctx.send")
async def ping(ctx: interaction.ApplicationContext):
    await ctx.send(f"pong — round trip {discord.utils.utcnow() - ctx.created_at}")


# ---------------------------------------------------------------- ephemeral
@interaction.command(name="secret", description="ephemeral response")
async def secret(ctx: interaction.ApplicationContext):
    await ctx.send("only you can see this", hidden=True)


# ---------------------------------------------------------------- defer / followup
@interaction.command(name="slow", description="defer -> edit -> followup")
async def slow(ctx: interaction.ApplicationContext):
    import asyncio

    await ctx.defer()
    await asyncio.sleep(2)
    await ctx.send("edited the deferred response")
    await ctx.send("and this is a followup message")


# ---------------------------------------------------------------- attachment
@interaction.command(name="file", description="attachment upload")
async def file_cmd(ctx: interaction.ApplicationContext):
    buf = io.BytesIO(b"discord-ext-interaction manual smoke test\n")
    await ctx.send("here is a file", file=discord.File(buf, filename="smoke.txt"))


# ---------------------------------------------------------------- components
@interaction.command(name="buttons", description="wait_for_component + detect_component")
async def buttons(ctx: interaction.ApplicationContext):
    await ctx.send(
        "press a button",
        components=[
            interaction.ActionRow(components=[
                interaction.Button(
                    label="wait_for", custom_id="smoke_wait",
                    style=discord.ButtonStyle.primary,
                ),
                interaction.Button(
                    label="detect", custom_id="smoke_detect",
                    style=discord.ButtonStyle.secondary,
                ),
            ])
        ],
    )
    result: interaction.ComponentsContext = await client.wait_for_component(
        "smoke_wait", timeout=30
    )
    await result.send(f"{result.author.mention} hit wait_for (custom_id={result.custom_id})")


@interaction.detect_component(custom_id="smoke_detect")
async def on_detect(ctx: interaction.ComponentsContext):
    await ctx.send(f"{ctx.author.mention} hit detect_component")


@client.listen()
async def on_components_cancelled(ctx: interaction.ComponentsContext):
    log.info("components_cancelled for custom_id=%s", ctx.custom_id)


# ---------------------------------------------------------------- modal (Action Row)
@interaction.command(name="form", description="modal via Action Row")
async def form(ctx: interaction.ApplicationContext):
    await ctx.modal(
        custom_id="smoke_form",
        title="Action Row modal",
        components=[
            interaction.ActionRow(components=[interaction.TextInput(
                custom_id="short", style=1, label="one line", required=True,
            )]),
            interaction.ActionRow(components=[interaction.TextInput(
                custom_id="long", style=2, label="paragraph", required=False,
            )]),
        ],
    )


# ---------------------------------------------------------------- modal (Label / type 18)
@interaction.command(name="form2", description="modal via Label component")
async def form2(ctx: interaction.ApplicationContext):
    await ctx.modal(
        custom_id="smoke_form2",
        title="Label modal",
        components=[
            interaction.Label(
                interaction.TextInput(custom_id="short", style=1, label="short"),
                label="one line", description="wrapped in a Label",
            ),
            interaction.Label(
                interaction.TextInput(custom_id="long", style=2, label="long"),
                label="paragraph",
            ),
        ],
    )


@client.listen()
async def on_modal(ctx: interaction.ModalSubmitContext):
    values = {c.custom_id: c.value for c in ctx.components}
    log.info("modal submit %s -> %s", ctx.custom_id, values)
    await ctx.send(f"received `{ctx.custom_id}`: {values}", hidden=True)


# ---------------------------------------------------------------- autocomplete
FRUITS = ("apple", "apricot", "banana", "blueberry", "cherry", "date")


@interaction.command(name="fruit", description="autocomplete")
@interaction.option(name="name", description="start typing", autocomplete=True)
async def fruit(ctx: interaction.ApplicationContext, name: str):
    await ctx.send(f"you picked: {name}")


@client.listen()
async def on_autocomplete(ctx: interaction.AutocompleteContext):
    current = str(ctx.options.get("name", "")).lower()
    matches = [f for f in FRUITS if current in f][:25]
    await ctx.autocomplete(
        [interaction.CommandOptionChoice(name=f, value=f) for f in matches]
    )


# ---------------------------------------------------------------- option resolution
@interaction.command(name="whoami", description="resolve a user option")
async def whoami(ctx: interaction.ApplicationContext, user: discord.User):
    # in a guild this resolves to a Member; joined_at is Member-only
    joined = getattr(user, "joined_at", None)
    await ctx.send(f"{user} (id {user.id}), joined {joined}")


for cmd in (ping, secret, slow, file_cmd, buttons, form, form2, fruit, whoami):
    client.add_interaction(cmd, sync_command=True)

client.run(TOKEN, log_handler=None)
