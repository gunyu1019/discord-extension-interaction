"""aiohttp endpoint for Discord's outgoing interaction webhooks."""

import json

from aiohttp import web

from .signature import InteractionSignatureVerifier


class AiohttpInteractionAdapter:
    """Verify HTTP interactions and route them through the Gateway dispatcher."""

    def __init__(self, client, public_key: str):
        self.client = client
        self.verifier = InteractionSignatureVerifier(public_key)

    async def handle(self, request: web.Request) -> web.StreamResponse:
        body = await request.read()
        if not self.verifier.verify(
            request.headers.get("X-Signature-Ed25519"),
            request.headers.get("X-Signature-Timestamp"), body,
        ):
            raise web.HTTPUnauthorized(text="invalid request signature")
        try:
            payload = json.loads(body)
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise web.HTTPBadRequest(text="invalid interaction JSON")
        if not isinstance(payload, dict):
            raise web.HTTPBadRequest(text="interaction must be a JSON object")
        if payload.get("type") == 1:
            return web.json_response({"type": 1})
        if payload.get("type") not in (2, 3, 4, 5):
            raise web.HTTPBadRequest(text="unsupported interaction type")
        self.client._interaction_dispatcher().route(payload)
        # The existing context callbacks use POST /interactions/.../callback.
        # Discord requires HTTP 202 with no body for that response mode.
        return web.Response(status=202)

    def register(self, app: web.Application, path: str = "/interactions") -> None:
        app.router.add_post(path, self.handle)
