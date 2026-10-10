"""Initial callback failures and followup transitions retain accurate state."""

import asyncio

import pytest

from discord.ext import interaction
from discord.ext.interaction import interaction as interaction_module
from discord.ext.interaction.application.response_state import ResponsePhase
from discord.ext.interaction.errors import AlreadyDeferred


def _context(offline_client, user_payload):
    return interaction.ApplicationContext({
        "id": "40", "application_id": "20", "type": 2, "token": "tk",
        "version": 1, "user": user_payload, "channel_id": "30",
        "data": {"id": "50", "name": "open", "type": 1},
    }, offline_client)


def test_expired_initial_callback_does_not_advance_state(offline_client, user_payload):
    context = _context(offline_client, user_payload)

    class ExpiredHTTP:
        async def post_initial_response(self, **kwargs):
            raise TimeoutError("interaction token expired")

    context.http = ExpiredHTTP()
    with pytest.raises(TimeoutError, match="expired"):
        asyncio.run(context.defer())
    assert context._response_state.phase is ResponsePhase.NEW
    assert not context.deferred and not context.responded


def test_defer_and_edit_consume_initial_once(monkeypatch, offline_client, user_payload):
    context = _context(offline_client, user_payload)

    class HTTP:
        async def post_initial_response(self, **kwargs):
            return None

        async def edit_initial_response(self, **kwargs):
            return {}

    monkeypatch.setattr(interaction_module, "Message", lambda **kwargs: kwargs)
    context.http = HTTP()
    asyncio.run(context.defer())
    with pytest.raises(AlreadyDeferred):
        asyncio.run(context.defer())
    asyncio.run(context.edit(content="done"))
    assert context._response_state.phase is ResponsePhase.RESPONDED
    assert context.responded and not context.deferred


def test_successful_callback_consumes_initial_if_message_fetch_fails(
    offline_client, user_payload,
):
    context = _context(offline_client, user_payload)

    class HTTP:
        async def post_initial_response(self, **kwargs):
            return None

        async def get_initial_response(self, **kwargs):
            raise TimeoutError("fetch failed")

    context.http = HTTP()
    with pytest.raises(TimeoutError, match="fetch failed"):
        asyncio.run(context.send(content="hello"))
    assert context.responded
    assert context._response_state.phase is ResponsePhase.RESPONDED
