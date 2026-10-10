"""New scope= declarations work on every existing command decorator."""

from discord.ext import interaction


def test_decorators_and_direct_models_share_scope():
    scope = interaction.GuildScope(42)

    @interaction.command(name="ping", description="Ping", scope=scope)
    async def ping(ctx):
        return None

    @interaction.user(name="Inspect", scope=scope)
    async def inspect_user(ctx):
        return None

    @interaction.context(name="Inspect Message", scope=scope)
    async def inspect_message(ctx):
        return None

    direct = interaction.SlashCommand(name="ping", description="Ping", scope=scope)
    assert ping.scope == direct.scope == scope
    assert ping.to_register_dict() == direct.to_register_dict()
    assert inspect_user.scope == scope
    assert inspect_message.scope == scope
