"""App-owned Activity commands dispatch and can launch their Activity."""

import asyncio
from types import SimpleNamespace

import pytest

from discord.ext import interaction
from discord.ext.interaction.implementation.response_state import ResponsePhase


def test_activity_command_dispatches_its_async_callback(offline_client):
    seen = []

    async def callback(context):
        seen.append(context.name)

    command = interaction.ActivityCommand(
        "launch", "Open the Activity", handler=interaction.ActivityHandler.APP_HANDLER,
    )
    offline_client.add_activity_command(command, callback)
    context = SimpleNamespace(
        application_type=4, name="launch", function=None, parents=None,
    )
    asyncio.run(offline_client.process_interaction(context))
    assert seen == ["launch"]


def test_activity_app_handler_requires_async_callback(offline_client):
    command = interaction.ActivityCommand(
        "launch", "Open", handler=interaction.ActivityHandler.APP_HANDLER,
    )
    with pytest.raises(TypeError, match="async callback"):
        offline_client.add_activity_command(command)


def test_launch_activity_sends_type_12_once(offline_client, user_payload):
    payload = {
        "id": "40", "application_id": "20", "type": 2, "token": "tk",
        "version": 1, "user": user_payload, "channel_id": "30",
        "data": {"id": "50", "name": "launch", "type": 4},
    }
    context = interaction.ApplicationContext(payload, offline_client)
    sent = []

    class HTTP:
        async def post_initial_response(self, *, payload, data):
            sent.append(payload)

    context.http = HTTP()
    asyncio.run(context.launch_activity())
    assert sent == [{"type": 12}]
    assert context._response_state.phase is ResponsePhase.RESPONDED
    with pytest.raises(RuntimeError, match="already responded"):
        asyncio.run(context.launch_activity())
