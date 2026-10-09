"""Public decorators pass Discord localization fields into command payloads."""

from discord.ext import interaction


def test_command_option_and_group_decorators_keep_localizations():
    @interaction.command(
        name="configure", description="Configure",
        name_localizations={"ko": "설정"},
        description_localizations={"ko": "구성 변경"},
    )
    async def configure(ctx):
        pass

    @configure.subcommand_group(
        name="theme", description="Theme",
        name_localizations={"ko": "테마"},
        description_localizations={"ko": "테마 설정"},
    )
    async def theme(ctx):
        pass

    @theme.subcommand(
        name="set", description="Set theme",
        name_localizations={"ko": "변경"},
        description_localizations={"ko": "테마 변경"},
    )
    @interaction.option(
        name="color", option_type=str, description="Color",
        name_localizations={"ko": "색상"},
        description_localizations={"ko": "색상을 선택"},
    )
    async def set_theme(ctx, color: str):
        pass

    configure.set_signature_option()
    payload = configure.to_register_dict()
    group_payload = payload["options"][0]
    subcommand_payload = group_payload["options"][0]
    option_payload = subcommand_payload["options"][0]

    assert payload["name_localizations"] == {"ko": "설정"}
    assert payload["description_localizations"] == {"ko": "구성 변경"}
    assert group_payload["name_localizations"] == {"ko": "테마"}
    assert subcommand_payload["name_localizations"] == {"ko": "변경"}
    assert option_payload["name_localizations"] == {"ko": "색상"}
    assert option_payload["description_localizations"] == {"ko": "색상을 선택"}


def test_user_and_message_context_decorators_keep_name_localizations():
    @interaction.user(name="Profile", name_localizations={"ko": "프로필"})
    async def profile(ctx):
        pass

    @interaction.context(name="Quote", name_localizations={"ko": "인용"})
    async def quote(ctx):
        pass

    assert profile.to_register_dict()["name_localizations"] == {"ko": "프로필"}
    assert quote.to_register_dict()["name_localizations"] == {"ko": "인용"}
