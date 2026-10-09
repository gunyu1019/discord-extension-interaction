"""Application command REST requests absent from discord.py's public HTTP helpers."""

from discord.http import Route


async def get_global_commands_with_localizations(http, application_id: int):
    """Fetch every global command with complete localization dictionaries."""
    route = Route(
        "GET", "/applications/{application_id}/commands",
        application_id=application_id,
    )
    return await http.request(route, params={"with_localizations": "true"})


async def get_guild_commands_with_localizations(
    http, application_id: int, guild_id: int
):
    """Fetch a guild's commands with full localization dictionaries."""
    route = Route(
        "GET", "/applications/{application_id}/guilds/{guild_id}/commands",
        application_id=application_id, guild_id=guild_id,
    )
    return await http.request(route, params={"with_localizations": "true"})


async def get_guild_command(
    http, application_id: int, guild_id: int, command_id: int
):
    """Fetch one guild command through discord.py's HTTP client."""
    return await http.get_guild_command(application_id, guild_id, command_id)
