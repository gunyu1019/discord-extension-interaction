"""Setup hooks and the fetched command cache honor their public contracts."""

import asyncio

from discord.ext.interaction.models.commands import from_payload
from discord.ext.interaction.models.enums import ApplicationCommandType


def test_remove_setup_hook_removes_only_requested_hook(offline_client):
    async def first():
        pass

    async def second():
        pass

    offline_client.add_setup_hook(first)
    offline_client.add_setup_hook(second)
    offline_client.remove_setup_hook(first)

    assert offline_client._multiple_setup_hook == [second]
    offline_client.remove_setup_hook(first)
    assert offline_client._multiple_setup_hook == [second]


def test_fetch_command_finds_cached_id_without_http(offline_client):
    cached = from_payload({
        "id": "100", "application_id": "200", "version": "300",
        "type": 1, "name": "ping", "description": "pong",
    })
    offline_client._fetch_interactions = offline_client._empty_command_map()
    offline_client._fetch_interactions[ApplicationCommandType.CHAT_INPUT][cached.name] = cached
    offline_client._pre_cached_application_id = 200

    class NoHTTP:
        async def get_global_command(self, **kwargs):
            raise AssertionError("cache hit must not call Discord")

    offline_client.http = NoHTTP()
    result = asyncio.run(offline_client.fetch_command(100, use_cached=True))

    assert result is cached


def test_fetch_command_populates_cache_after_http_miss(offline_client):
    payload = {
        "id": "100", "application_id": "200", "version": "300",
        "type": 1, "name": "ping", "description": "pong",
    }
    called = []

    class StubHTTP:
        async def get_global_command(self, **kwargs):
            called.append(kwargs)
            return payload

    offline_client._pre_cached_application_id = 200
    offline_client._fetch_interactions = offline_client._empty_command_map()
    offline_client.http = StubHTTP()

    result = asyncio.run(offline_client.fetch_command(100, use_cached=True))
    cached = asyncio.run(offline_client.fetch_command(100, use_cached=True))

    assert cached is result
    assert len(called) == 1
