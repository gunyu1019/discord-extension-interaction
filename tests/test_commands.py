"""ApplicationCommand payload parsing / serialisation / equality."""
import pytest

from discord.ext import interaction
from discord.ext.interaction.commands import ApplicationCommand, SlashCommand, from_payload
from discord.ext.interaction.enums import (
    ApplicationCommandType,
    ApplicationContextType,
    ApplicationIntegrationType,
)

MINIMAL = {
    "id": "100",
    "application_id": "200",
    "version": "300",
    "type": 1,
    "name": "ping",
    "description": "pong",
}
FULL = {
    **MINIMAL,
    "name": "manage",
    "nsfw": True,
    "integration_types": [0, 1],
    "contexts": [0, 1, 2],
}


def test_from_payload_without_optional_fields_does_not_raise():
    cmd = from_payload(MINIMAL)
    assert isinstance(cmd, SlashCommand)
    assert cmd.integration_types == []
    assert cmd.contexts == []
    assert cmd.nsfw is False
    assert cmd.type is ApplicationCommandType.CHAT_INPUT


def test_from_payload_maps_list_enums_elementwise():
    cmd = from_payload(FULL)
    assert cmd.integration_types == [
        ApplicationIntegrationType.GUILD_INSTALL,
        ApplicationIntegrationType.USER_INSTALL,
    ]
    assert all(isinstance(x, ApplicationContextType) for x in cmd.contexts)
    assert cmd.nsfw is True


def test_null_context_list_becomes_empty():
    cmd = from_payload({**MINIMAL, "contexts": None, "integration_types": None})
    assert cmd.contexts == [] and cmd.integration_types == []


def test_to_register_dict_emits_int_lists_and_round_trips():
    reg = from_payload(FULL).to_register_dict()
    assert reg["integration_types"] == [0, 1]
    assert reg["contexts"] == [0, 1, 2]
    assert all(type(x) is int for x in reg["contexts"] + reg["integration_types"])


def test_to_register_dict_tolerates_raw_int_constructor_args():
    cmd = ApplicationCommand(
        name="x", description="y", contexts=[0], integration_types=[1]
    )
    reg = cmd.to_register_dict()
    assert reg["contexts"] == [0]
    assert reg["integration_types"] == [1]


def test_equality_ignores_server_assigned_version():
    a = from_payload({**FULL, "version": "111"})
    b = from_payload({**FULL, "version": "999"})
    assert a == b


def test_equality_still_detects_real_differences():
    a = from_payload(FULL)
    b = from_payload({**FULL, "nsfw": False})
    assert a != b


def test_decorator_command_matches_its_fetched_form():
    @interaction.command(name="ping", description="pong")
    async def ping(ctx):
        ...

    ping.set_signature_option()  # normally performed by add_interaction
    fetched = from_payload(MINIMAL)
    assert ping == fetched
