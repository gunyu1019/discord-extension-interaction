"""Signed outgoing webhooks reach the shared interaction dispatcher."""

import asyncio
import json
from types import SimpleNamespace

from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer
from nacl.signing import SigningKey

from discord.ext.interaction.transport.aiohttp_interactions import AiohttpInteractionAdapter
from discord.ext import interaction


def test_signed_application_command_routes_and_returns_202():
    key = SigningKey.generate()
    received = []
    dispatcher = SimpleNamespace(route=lambda payload: received.append(payload))
    client = SimpleNamespace(_interaction_dispatcher=lambda: dispatcher)
    adapter = AiohttpInteractionAdapter(client, key.verify_key.encode().hex())
    app = web.Application()
    adapter.register(app, "/discord")

    async def run():
        async with TestClient(TestServer(app)) as http:
            body = json.dumps({"type": 2, "data": {"name": "hello"}}).encode()
            timestamp = "1700000000"
            signature = key.sign(timestamp.encode() + body).signature.hex()
            response = await http.post("/discord", data=body, headers={
                "X-Signature-Ed25519": signature,
                "X-Signature-Timestamp": timestamp,
            })
            assert response.status == 202
            assert await response.read() == b""

    asyncio.run(run())
    assert received == [{"type": 2, "data": {"name": "hello"}}]


def test_ping_requires_valid_signature_and_returns_json_pong():
    key = SigningKey.generate()
    received = []
    client = SimpleNamespace(_interaction_dispatcher=lambda: SimpleNamespace(
        route=lambda payload: received.append(payload),
    ))
    app = web.Application()
    AiohttpInteractionAdapter(client, key.verify_key.encode().hex()).register(app)

    async def run():
        async with TestClient(TestServer(app)) as http:
            body = b'{"type":1}'
            timestamp = "1700000000"
            signature = key.sign(timestamp.encode() + body).signature.hex()
            headers = {
                "X-Signature-Ed25519": signature,
                "X-Signature-Timestamp": timestamp,
            }
            assert (await http.post("/interactions", data=body)).status == 401
            assert (await http.post("/interactions", data=b'{"type":2}', headers=headers)).status == 401
            response = await http.post("/interactions", data=body, headers=headers)
            assert response.status == 200
            assert response.content_type == "application/json"
            assert await response.json() == {"type": 1}

    asyncio.run(run())
    assert received == []


def test_inline_response_uses_context_without_publishing_gateway_event():
    key = SigningKey.generate()
    routed = []

    class Dispatcher:
        def route(self, payload, *, publish=True):
            routed.append((payload["type"], publish))
            return SimpleNamespace(name=payload["data"]["name"])

    async def inline_handler(context):
        return {"type": 4, "data": {"content": context.name}}

    client = SimpleNamespace(_interaction_dispatcher=Dispatcher)
    app = web.Application()
    AiohttpInteractionAdapter(
        client, key.verify_key.encode().hex(), inline_handler=inline_handler,
    ).register(app)

    async def run():
        async with TestClient(TestServer(app)) as http:
            body = b'{"type":2,"data":{"name":"hello"}}'
            timestamp = "1700000000"
            signature = key.sign(timestamp.encode() + body).signature.hex()
            response = await http.post("/interactions", data=body, headers={
                "X-Signature-Ed25519": signature,
                "X-Signature-Timestamp": timestamp,
            })
            assert response.status == 200
            assert await response.json() == {"type": 4, "data": {"content": "hello"}}

    asyncio.run(run())
    assert routed == [(2, False)]


def test_signed_http_command_uses_real_client_dispatcher(offline_client, user_payload):
    key = SigningKey.generate()

    async def callback(context):
        return None

    command = interaction.Command(callback, name="ping", description="Ping")
    offline_client.add_interaction(command, sync_command=False)
    dispatched = []
    offline_client._connection.dispatch = lambda event, context: dispatched.append(
        (event, context.name)
    )
    app = web.Application()
    AiohttpInteractionAdapter(
        offline_client, key.verify_key.encode().hex(),
    ).register(app)

    async def run():
        async with TestClient(TestServer(app)) as http:
            payload = {
                "id": "40", "application_id": "20", "type": 2, "token": "tk",
                "version": 1, "user": user_payload, "channel_id": "30",
                "data": {"id": "50", "name": "ping", "type": 1},
            }
            body = json.dumps(payload).encode()
            timestamp = "1700000000"
            signature = key.sign(timestamp.encode() + body).signature.hex()
            response = await http.post("/interactions", data=body, headers={
                "X-Signature-Ed25519": signature,
                "X-Signature-Timestamp": timestamp,
            })
            assert response.status == 202

    asyncio.run(run())
    assert dispatched == [("interaction_command", "ping")]
