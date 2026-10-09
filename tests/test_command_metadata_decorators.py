"""Decorated commands expose the same metadata as direct command models."""

import pytest

from discord.ext import interaction


@pytest.mark.parametrize(
    "decorator, direct_class",
    [
        (interaction.command, interaction.SlashCommand),
        (interaction.user, interaction.UserCommand),
        (interaction.context, interaction.ContextMenu),
    ],
)
def test_decorated_command_metadata_matches_direct_model(decorator, direct_class):
    metadata = {
        "default_member_permissions": "0",
        "nsfw": True,
        "integration_types": [interaction.ApplicationIntegrationType.GUILD_INSTALL],
        "contexts": [interaction.ApplicationContextType.GUILD],
    }

    if decorator is interaction.command:
        declared = decorator(name="inspect", description="Inspect", **metadata)
        direct = direct_class(name="inspect", description="Inspect", **metadata)
    else:
        declared = decorator(name="Inspect", **metadata)
        direct = direct_class(name="Inspect", **metadata)

    @declared
    async def inspect(ctx):
        pass

    if decorator is interaction.command:
        inspect.set_signature_option()

    assert inspect.to_register_dict() == direct.to_register_dict()
