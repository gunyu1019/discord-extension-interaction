"""V2 models reach ordinary and interaction message HTTP send/edit calls."""

import asyncio
from types import SimpleNamespace

from discord.ext import interaction
from discord.ext.interaction import interaction as interaction_module
from discord.ext.interaction import message as message_module


def test_regular_send_and_edit_forward_v2_payload(monkeypatch):
    sent = {}

    class HTTP:
        async def send_message(self, *, params, channel_id):
            sent["send"] = params.payload
            return {}

        async def edit_message(self, *, params, channel_id, message_id):
            sent["edit"] = params.payload

    monkeypatch.setattr(message_module, "Message", lambda **kwargs: kwargs)
    state = SimpleNamespace(http=HTTP(), allowed_mentions=None)
    channel = SimpleNamespace(id=7, _state=state)
    display = interaction.TextDisplay("Hello")

    asyncio.run(interaction.MessageTransferable(state, channel).send(components=[display]))
    asyncio.run(interaction.MessageEditable(channel, 9).edit(components=[display]))
    assert sent["send"]["flags"] & 32768
    assert sent["edit"]["flags"] & 32768
    assert sent["edit"]["components"] == [display.to_payload()]


def test_interaction_send_and_edit_forward_v2_payload(monkeypatch, offline_client, user_payload):
    payload = {
        "id": "40", "application_id": "20", "type": 2, "token": "tk",
        "version": 1, "user": user_payload, "channel_id": "30",
        "data": {"id": "50", "name": "open", "type": 1},
    }
    context = interaction.ApplicationContext(payload, offline_client)
    sent = {}

    class HTTP:
        async def post_initial_response(self, *, payload, data):
            sent["send"] = payload

        async def get_initial_response(self, *, data):
            return {}

        async def edit_initial_response(self, *, payload, form, files, data):
            sent["edit"] = payload
            return {}

    monkeypatch.setattr(interaction_module, "Message", lambda **kwargs: kwargs)
    context.http = HTTP()
    display = interaction.TextDisplay("Hello")

    asyncio.run(context.send(components=[display]))
    asyncio.run(context.edit(components=[display]))
    assert sent["send"]["data"]["flags"] & 32768
    assert sent["edit"]["flags"] & 32768
    assert sent["edit"]["components"] == [display.to_payload()]
