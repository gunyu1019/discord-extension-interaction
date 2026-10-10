"""Modal submissions preserve each Discord Select Menu's selected IDs."""

import pytest

from discord.ext import interaction


@pytest.mark.parametrize("component_type,model", [
    (3, interaction.Selection),
    (5, interaction.UserSelect),
    (6, interaction.RoleSelect),
    (7, interaction.MentionableSelect),
    (8, interaction.ChannelSelect),
])
def test_modal_select_values_survive_label_parsing(
    offline_client, user_payload, component_type, model,
):
    payload = {
        "id": "40", "application_id": "20", "type": 5, "token": "tk",
        "version": 1, "user": user_payload, "channel_id": "30",
        "data": {"custom_id": "survey", "components": [{
            "type": 18, "component": {
                "type": component_type, "custom_id": "answer", "values": ["42"],
            },
        }]},
    }
    context = interaction.ModalSubmitContext(payload, offline_client)
    submitted = context.components[0]
    assert isinstance(submitted, model)
    assert submitted.values == ["42"]
    serialized = submitted.to_dict() if component_type == 3 else submitted.to_payload()
    assert "values" not in serialized
