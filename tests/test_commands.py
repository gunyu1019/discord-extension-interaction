"""ApplicationCommand payload parsing / serialisation / equality."""
import pytest

from discord.ext import interaction
from discord.ext.interaction.models.commands import ApplicationCommand, ApplicationSubcommand, ApplicationSubcommandGroup, CommandOption, CommandOptionChoice, SlashCommand, from_payload
from discord.ext.interaction.models.enums import ApplicationCommandType, ApplicationContextType, ApplicationIntegrationType

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
    assert reg["nsfw"] is True
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


def test_command_metadata_registration_fields_and_round_trip():
    command = ApplicationCommand(
        name="restricted",
        description="restricted command",
        default_member_permissions="0",
        nsfw=True,
        integration_types=[ApplicationIntegrationType.GUILD_INSTALL],
        contexts=[ApplicationContextType.GUILD],
    )
    fields = command.to_register_dict()

    assert fields["default_member_permissions"] == "0"
    assert fields["nsfw"] is True
    assert fields["integration_types"] == [0]
    assert fields["contexts"] == [0]

    received = from_payload({**MINIMAL, **fields})
    assert received.default_member_permissions == "0"
    assert received.nsfw is True
    assert received.integration_types == [ApplicationIntegrationType.GUILD_INSTALL]
    assert received.contexts == [ApplicationContextType.GUILD]


def test_command_metadata_default_is_not_nsfw():
    fields = ApplicationCommand(name="public", description="safe").to_register_dict()
    assert "nsfw" not in fields
    assert "default_member_permissions" not in fields


def test_command_localizations_round_trip_and_affect_comparison():
    command = SlashCommand(
        name="hello", description="say hello",
        name_localizations={"ko": "안녕"},
        description_localizations={"ko": "인사합니다"},
    )
    payload = command.to_register_dict()
    assert payload["name_localizations"] == {"ko": "안녕"}
    assert payload["description_localizations"] == {"ko": "인사합니다"}

    restored = from_payload({**MINIMAL, **payload})
    assert restored.name_localizations == command.name_localizations
    assert restored.description_localizations == command.description_localizations
    assert command == restored
    restored.name_localizations["ko"] = "반갑습니다"
    assert command != restored


def test_choice_name_localizations_round_trip_and_affect_comparison():
    choice = CommandOptionChoice(
        name="Red", value="red", name_localizations={"ko": "빨강"}
    )
    restored = CommandOptionChoice.from_payload(choice.to_dict())
    assert restored.to_dict()["name_localizations"] == {"ko": "빨강"}
    assert restored == choice
    restored.name_localizations["ko"] = "붉은색"
    assert restored != choice


def test_nested_option_and_subcommand_localizations_round_trip():
    option = CommandOption(
        name="color", option_type=str, description="Choose a color",
        name_localizations={"ko": "색상"},
        description_localizations={"ko": "색상을 고르세요"},
        choices=[CommandOptionChoice("Red", "red", {"ko": "빨강"})],
    )
    subcommand = ApplicationSubcommand(
        name="set", description="Set color", options=[option],
        name_localizations={"ko": "설정"},
        description_localizations={"ko": "색상 설정"},
    )
    group = ApplicationSubcommandGroup(
        name="theme", description="Theme options", options=[subcommand],
        name_localizations={"ko": "테마"},
        description_localizations={"ko": "테마 옵션"},
    )
    command = SlashCommand(name="configure", description="Configure", options=[group])

    payload = command.to_register_dict()
    restored = from_payload({**MINIMAL, **payload})

    assert restored == command
    assert payload["options"][0]["name_localizations"] == {"ko": "테마"}
    assert payload["options"][0]["options"][0]["name_localizations"] == {"ko": "설정"}
    assert payload["options"][0]["options"][0]["options"][0]["choices"][0]["name_localizations"] == {"ko": "빨강"}
    restored.options[0].options[0].options[0].description_localizations["ko"] = "다른 설명"
    assert restored != command


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
