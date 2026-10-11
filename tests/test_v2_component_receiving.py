"""Received Components V2 trees are restored as public component models."""

import asyncio

from discord.ext import interaction
from discord.ext.interaction.implementation.components import from_payload


def test_received_container_restores_nested_v2_models():
    source = interaction.Container([
        interaction.MediaGallery([
            interaction.MediaGalleryItem(
                interaction.UnfurledMediaItem("https://example.com/a.png")
            )
        ]),
        interaction.Section(
            [interaction.TextDisplay("Caption")],
            interaction.Thumbnail(interaction.UnfurledMediaItem("https://example.com/a.png")),
        ),
    ]).to_payload()
    received = from_payload([source])[0]
    assert isinstance(received, interaction.Container)
    assert isinstance(received.components[0], interaction.MediaGallery)
    assert isinstance(received.components[1].accessory, interaction.Thumbnail)
    assert received.to_payload() == source


def test_message_send_forwards_v2_components(monkeypatch):
    captured = {}

    async def fake_send(self, *args, **kwargs):
        captured.update(kwargs)

    monkeypatch.setattr(interaction.MessageTransferable, "send", fake_send)
    message = type("MessageStub", (), {"_state": object(), "channel": object()})()
    display = interaction.TextDisplay("Hello")
    asyncio.run(interaction.Message.send(message, components=[display]))
    assert captured["components"] == [display]


def test_modal_send_accepts_text_display(offline_client, user_payload):
    payload = {
        "id": "40", "application_id": "20", "type": 2, "token": "tk",
        "version": 1, "user": user_payload, "channel_id": "30",
        "data": {"id": "50", "name": "open", "type": 1},
    }
    context = interaction.ApplicationContext(payload, offline_client)
    sent = {}

    class HTTP:
        async def request(self, route, **kwargs):
            sent["json"] = kwargs.get("json")
            return {}

    context.http.http = HTTP()
    asyncio.run(context.modal(
        "survey", "Survey", [
            interaction.TextDisplay("Choose an answer"),
            interaction.Label(interaction.TextInput("answer", 1), label="Answer"),
        ],
    ))
    assert sent["json"]["data"]["components"][0] == {
        "type": 10, "content": "Choose an answer"
    }
