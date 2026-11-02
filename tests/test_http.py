"""InteractionHTTPClient — route construction and rate-limit bucketing."""
import asyncio

from discord.ext.interaction.interaction_api import InteractionData, InteractionHTTPClient


class _RecordingHTTP:
    """Stands in for ``discord.http.HTTPClient`` — records requests, no I/O."""

    def __init__(self):
        self.calls = []

    async def request(self, route, **kwargs):
        self.calls.append(
            {
                "method": route.method,
                "path": route.path,
                "url": route.url,
                "major": route.major_parameters,
                "kwargs": set(kwargs),
            }
        )
        return {"ok": True}


DATA = InteractionData(id=123, application_id=456, token="tok")


def _run(coro):
    return asyncio.run(coro)


def test_interaction_data_fields():
    assert (DATA.id, DATA.application_id, DATA.token) == (123, 456, "tok")


def test_initial_response_hits_callback_endpoint():
    http = _RecordingHTTP()
    client = InteractionHTTPClient(http)
    _run(client.post_initial_response(DATA, {"type": 5}))

    call = http.calls[0]
    assert call["method"] == "POST"
    assert call["path"] == "/interactions/{webhook_id}/{webhook_token}/callback"
    assert call["url"].endswith("/interactions/123/tok/callback")
    assert call["kwargs"] == {"json"}
    # bucketed by interaction id + token
    assert "123" in call["major"] and "tok" in call["major"]


def test_original_response_uses_application_id_and_bakes_at_original():
    http = _RecordingHTTP()
    client = InteractionHTTPClient(http)
    _run(client.get_initial_response(DATA))
    _run(client.edit_initial_response(DATA, payload={"content": "x"}))
    _run(client.delete_initial_response(DATA))

    for call in http.calls:
        # @original must be part of the path, never a formatted parameter,
        # otherwise Route percent-encodes '@' to %40 and Discord 404s.
        assert call["path"].endswith("/messages/@original")
        assert call["url"].endswith("/messages/@original")
        assert "%40" not in call["url"]
        assert "/webhooks/456/tok/" in call["url"]


def test_edit_initial_response_forwards_multipart_when_form_present():
    http = _RecordingHTTP()
    client = InteractionHTTPClient(http)
    _run(
        client.edit_initial_response(
            DATA,
            form=[{"name": "payload_json", "value": "{}"}],
            files=[],
        )
    )
    assert http.calls[0]["kwargs"] == {"form", "files"}


def test_followup_routes_use_real_message_id():
    http = _RecordingHTTP()
    client = InteractionHTTPClient(http)
    _run(client.post_followup(DATA, payload={"content": "f"}))
    _run(client.edit_followup(DATA, "999", payload={"content": "fe"}))
    _run(client.delete_followup(DATA, "999"))

    post, edit, delete = http.calls
    assert post["url"].endswith("/webhooks/456/tok")
    assert edit["url"].endswith("/webhooks/456/tok/messages/999")
    assert delete["url"].endswith("/webhooks/456/tok/messages/999")
