"""Guild command transport calls the corresponding Discord REST endpoints."""

import asyncio

from discord.ext.interaction.transport.command_api import (
    get_guild_command,
    get_guild_commands_with_localizations,
)


def test_guild_command_list_requests_full_localizations():
    calls = []

    class StubHTTP:
        async def request(self, route, **kwargs):
            calls.append((route, kwargs))
            return []

    result = asyncio.run(get_guild_commands_with_localizations(StubHTTP(), 200, 300))
    route, kwargs = calls[0]
    assert result == []
    assert route.method == "GET"
    assert route.url.endswith("/applications/200/guilds/300/commands")
    assert kwargs["params"] == {"with_localizations": "true"}


def test_guild_command_get_uses_guild_endpoint():
    calls = []

    class StubHTTP:
        async def get_guild_command(self, *args):
            calls.append(args)
            return {"id": "400"}

    result = asyncio.run(get_guild_command(StubHTTP(), 200, 300, 400))
    assert result == {"id": "400"}
    assert calls == [(200, 300, 400)]
