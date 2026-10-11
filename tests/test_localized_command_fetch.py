"""Command list requests include all locale dictionaries for accurate comparison."""

import asyncio

from discord.ext.interaction.models.enums import ApplicationCommandType


def test_fetch_commands_requests_complete_localizations(offline_client):
    requests = []

    class StubHTTP:
        async def request(self, route, **kwargs):
            requests.append((route, kwargs))
            return [{
                "id": "100", "application_id": "200", "version": "300",
                "type": 1, "name": "hello", "description": "say hello",
                "name_localizations": {"ko": "안녕"},
                "description_localizations": {"ko": "인사합니다"},
            }]

    offline_client.http = StubHTTP()
    offline_client._pre_cached_application_id = 200

    commands = asyncio.run(offline_client.fetch_commands())

    route, kwargs = requests[0]
    assert route.method == "GET"
    assert route.url.endswith("/applications/200/commands")
    assert kwargs["params"] == {"with_localizations": "true"}
    command = commands[ApplicationCommandType.CHAT_INPUT]["hello"]
    assert command.name_localizations == {"ko": "안녕"}
    assert command.description_localizations == {"ko": "인사합니다"}
