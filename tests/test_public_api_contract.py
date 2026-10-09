"""Protect the documented entry points while internals are split into modules."""

import discord

from discord.ext import interaction


def test_readme_command_registration_without_network():
    client = interaction.Client(
        global_sync_command=False, intents=discord.Intents.none()
    )

    @interaction.command(name="ping", description="Respond with pong")
    async def ping(ctx: interaction.ApplicationContext):
        await ctx.send("pong")

    client.add_interaction(ping)

    assert client.get_interaction() == [ping]
    assert ping.to_register_dict() == {
        "name": "ping",
        "type": interaction.ApplicationCommandType.CHAT_INPUT.value,
        "description": "Respond with pong",
        "options": [],
    }


def test_existing_component_names_are_importable():
    assert interaction.ActionRow is not None
    assert interaction.Button is not None
    assert interaction.Selection is not None
    assert interaction.TextInput is not None
    assert interaction.Label is not None
    assert interaction.ModalSubmitContext is not None
