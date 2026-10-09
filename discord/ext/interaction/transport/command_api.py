"""Application command REST requests absent from discord.py's public HTTP helpers."""

from discord.http import Route


async def get_global_commands_with_localizations(http, application_id: int):
    """Fetch every global command with complete localization dictionaries."""
    route = Route(
        "GET", "/applications/{application_id}/commands",
        application_id=application_id,
    )
    return await http.request(route, params={"with_localizations": "true"})
