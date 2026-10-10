"""Signed outgoing webhooks reach the shared interaction dispatcher."""

import asyncio
import json
from types import SimpleNamespace

from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer
from nacl.signing import SigningKey

from discord.ext.interaction.transport.aiohttp_interactions import AiohttpInteractionAdapter


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
