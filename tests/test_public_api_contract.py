"""Protect the documented entry points after reorganizing the package."""

import discord

from discord.ext import interaction
from discord.ext.interaction.models import legacy_components


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


def test_existing_component_facade_keeps_class_identity_and_to_dict():
    assert interaction.ActionRow is legacy_components.ActionRow
    assert interaction.Button is legacy_components.Button
    assert interaction.Label is legacy_components.Label
    assert interaction.SelectOption is legacy_components.SelectOption
    assert interaction.Selection is legacy_components.Selection
    assert interaction.TextInput is legacy_components.TextInput

    item = interaction.Button(style=1, label="Open", custom_id="open")
    row = interaction.ActionRow([item])
    assert item.to_dict() == {
        "type": 2, "style": 1, "label": "Open", "custom_id": "open"
    }
    assert row.to_dict()["components"] == [item]
    assert row.to_all_dict()["components"] == [item.to_dict()]
