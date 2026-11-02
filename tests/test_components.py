"""Component parsing — Action Row and Label modal submissions."""
import asyncio

import discord
import pytest

from discord.ext import interaction
from discord.ext.interaction.components import Label, TextInput, from_payload

LABEL_PAYLOAD = {
    "type": 18,
    "label": "Your name",
    "description": "as it appears on file",
    "component": {
        "type": 4,
        "custom_id": "name",
        "style": 1,
        "label": "n",
        "value": "Ada",
    },
}


def test_from_payload_builds_label_and_unwraps_child():
    parsed = from_payload([LABEL_PAYLOAD])
    assert len(parsed) == 1 and isinstance(parsed[0], Label)
    label = parsed[0]
    assert label.label == "Your name"
    assert label.description == "as it appears on file"
    assert isinstance(label.component, TextInput)
    assert label.component.custom_id == "name"
    assert label.component.value == "Ada"
    # same list shape as ActionRow.components
    assert label.components == [label.component]


def test_label_round_trips_for_sending():
    rt = from_payload([LABEL_PAYLOAD])[0].to_all_dict()
    assert rt["type"] == 18
    assert rt["label"] == "Your name"
    assert rt["component"]["type"] == 4
    assert rt["component"]["custom_id"] == "name"


def test_label_strips_label_and_description_from_its_child():
    # Discord rejects `label` / `description` set on a component inside a Label.
    label = Label(
        TextInput(custom_id="x", style=1, label="dummy"),
        label="real label",
        description="real description",
    )
    child = label.to_all_dict()["component"]
    assert "label" not in child
    assert "description" not in child


def test_text_input_label_is_optional():
    ti = TextInput(custom_id="x", style=1)
    assert ti.label is None
    assert "label" not in ti.to_dict()


def _submit_frame(components, user_payload):
    return {
        "id": "10",
        "application_id": "20",
        "type": 5,
        "token": "tk",
        "version": 1,
        "user": user_payload,
        "channel_id": "30",
        "locale": "en-US",
        "data": {"custom_id": "profile", "components": components},
    }


@pytest.mark.parametrize(
    "wrapper",
    [
        pytest.param(
            [
                {
                    "type": 1,
                    "components": [
                        {"type": 4, "custom_id": "bio", "style": 2, "label": "b", "value": "v"}
                    ],
                }
            ],
            id="action-row",
        ),
        pytest.param(
            [
                {
                    "type": 18,
                    "component": {
                        "type": 4,
                        "custom_id": "bio",
                        "style": 2,
                        "label": "b",
                        "value": "v",
                    },
                }
            ],
            id="label",
        ),
    ],
)
def test_modal_submit_unwraps_both_formats(offline_client, user_payload, wrapper):
    ctx = interaction.ModalSubmitContext(
        _submit_frame(wrapper, user_payload), offline_client
    )
    assert ctx.custom_id == "profile"
    assert [c.custom_id for c in ctx.components] == ["bio"]
    assert ctx.components[0].value == "v"


def test_modal_submit_handles_mixed_and_bare_leaves(offline_client, user_payload):
    components = [
        {"type": 1, "components": [
            {"type": 4, "custom_id": "a", "style": 1, "label": "a", "value": "1"}]},
        {"type": 18, "component":
            {"type": 4, "custom_id": "b", "style": 1, "label": "b", "value": "2"}},
        {"type": 4, "custom_id": "c", "style": 1, "label": "c", "value": "3"},
    ]
    ctx = interaction.ModalSubmitContext(
        _submit_frame(components, user_payload), offline_client
    )
    assert [c.custom_id for c in ctx.components] == ["a", "b", "c"]
    assert [c.value for c in ctx.components] == ["1", "2", "3"]


def test_modal_send_path_serialises_label(offline_client, user_payload):
    app_frame = {
        "id": "40",
        "application_id": "20",
        "type": 2,
        "token": "tk2",
        "version": 1,
        "user": user_payload,
        "channel_id": "30",
        "locale": "en-US",
        "data": {"id": "50", "name": "open", "type": 1},
    }
    ctx = interaction.ApplicationContext(app_frame, offline_client)

    sent = {}

    class _HTTP:
        async def request(self, route, **kw):
            sent["json"] = kw.get("json")
            return {}

    ctx.http.http = _HTTP()
    asyncio.run(
        ctx.modal(
            "m1",
            "Title",
            [Label(TextInput(custom_id="x", style=1, label="X"), label="Field X")],
        )
    )
    component = sent["json"]["data"]["components"][0]
    assert component["type"] == 18
    assert component["label"] == "Field X"
    assert component["component"]["custom_id"] == "x"


def test_label_is_publicly_exported():
    assert interaction.Label is Label
