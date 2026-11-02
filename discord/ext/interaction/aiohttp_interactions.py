"""aiohttp endpoint for Discord's outgoing interaction webhooks."""

import json
import asyncio
import logging
from collections.abc import Awaitable, Callable

from aiohttp import web

from discord.ext.interaction.signature import (
    InteractionSignatureVerifier,
)
from discord.ext.interaction.response_payload import (
    validate_inline_response,
)

log = logging.getLogger(__name__)


class AiohttpInteractionAdapter:
    """Verify HTTP interactions and route them through the Gateway dispatcher."""

    def __init__(
        self,
        client,
        public_key: str,
        *,
        inline_handler: Callable[[object], Awaitable[dict]] | None = None,
    ):
        self.client = client
        self.verifier = InteractionSignatureVerifier(public_key)
        self.inline_handler = inline_handler

    async def handle(self, request: web.Request) -> web.StreamResponse:
        body = await request.read()
        if not self.verifier.verify(
            request.headers.get("X-Signature-Ed25519"),
            request.headers.get("X-Signature-Timestamp"),
            body,
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
        dispatcher = self.client._interaction_dispatcher()
        if self.inline_handler is not None:
            context = dispatcher.route(payload, publish=False)
            if context is None:
                raise web.HTTPBadRequest(text="unsupported interaction type")
            try:
                response = await asyncio.wait_for(
                    self.inline_handler(context), timeout=2.5
                )
                validate_inline_response(payload["type"], response)
            except asyncio.TimeoutError as error:
                log.warning("inline interaction handler timed out")
                raise web.HTTPInternalServerError(
                    text="inline interaction handler timed out"
                ) from error
            except ValueError as error:
                # The message may come from user code; keep it in the log only.
                log.warning("invalid inline interaction response: %s", error)
                raise web.HTTPInternalServerError(
                    text="invalid inline interaction response"
                ) from error
            if hasattr(context, "_response_state"):
                context._response_state.responded()
                context.responded = True
            return web.json_response(response)
        dispatcher.route(payload)
        # The existing context callbacks use POST /interactions/.../callback.
        # Discord requires HTTP 202 with no body for that response mode.
        return web.Response(status=202)

    def register(self, app: web.Application, path: str = "/interactions") -> None:
        app.router.add_post(path, self.handle)
