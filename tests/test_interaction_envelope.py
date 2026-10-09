"""Gateway and HTTP payloads share a pure Discord interaction snapshot."""

from dataclasses import FrozenInstanceError

import pytest

from discord.ext.interaction.domain.interaction import InteractionEnvelope


def test_ping_can_omit_data_and_optional_context():
    envelope = InteractionEnvelope.from_payload({
        "id": "100", "application_id": "200", "type": 1,
        "token": "token", "version": 1,
    })

    assert envelope.id == 100
    assert envelope.application_id == 200
    assert envelope.type == 1
    assert envelope.data is None
    assert envelope.guild_id is None
    assert envelope.entitlements == ()
    assert envelope.authorizing_integration_owners == {}


def test_common_fields_and_unknown_fields_survive_a_payload_snapshot():
    payload = {
        "id": "100", "application_id": "200", "type": 3,
        "token": "token", "version": 1,
        "data": {"custom_id": "approve", "component_type": 2},
        "guild_id": "300", "channel_id": "400",
        "guild": {"id": "300"}, "channel": {"id": "400"},
        "member": {"user": {"id": "500"}},
        "message": {"id": "600"},
        "app_permissions": "8", "locale": "ko", "guild_locale": "en-US",
        "entitlements": [{"id": "700"}],
        "authorizing_integration_owners": {"0": "300"},
        "context": 0, "attachment_size_limit": 26214400,
        "future_discord_field": {"nested": [1]},
    }
    envelope = InteractionEnvelope.from_payload(payload)
    payload["data"]["custom_id"] = "changed"
    payload["future_discord_field"]["nested"].append(2)

    assert envelope.guild_id == 300
    assert envelope.channel_id == 400
    assert envelope.data == {"custom_id": "approve", "component_type": 2}
    assert envelope.member["user"]["id"] == "500"
    assert envelope.entitlements == ({"id": "700"},)
    assert envelope.authorizing_integration_owners == {"0": "300"}
    assert envelope.attachment_size_limit == 26214400
    assert envelope.raw_payload["future_discord_field"] == {"nested": [1]}

    with pytest.raises(FrozenInstanceError):
        envelope.type = 5


def test_future_interaction_type_is_preserved():
    envelope = InteractionEnvelope.from_payload({
        "id": "100", "application_id": "200", "type": 99,
        "token": "token", "version": 1, "data": {"new": True},
    })
    assert envelope.type == 99
    assert envelope.data == {"new": True}
