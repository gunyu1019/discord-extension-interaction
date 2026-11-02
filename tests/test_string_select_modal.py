"""The existing Selection API can render a modal String Select."""

import pytest

from discord.ext import interaction
from discord.ext.interaction.component_validation import validate_modal_components
from discord.ext.interaction.parser import handle_message_parameter


def test_modal_string_select_serializes_required_without_disabled():
    select = interaction.Selection(
        custom_id="pet", options=[interaction.SelectOption("Cat", "cat")],
        required=False,
    )
    label = interaction.Label(select, label="Pet")
    child = label.to_all_dict()["component"]
    assert child["required"] is False
    assert "disabled" not in child
    assert interaction.Selection.from_dict(select.to_dict()).required is False


def test_string_select_defaults_and_bounds_are_validated():
    valid = interaction.Selection("pick", [interaction.SelectOption("A", "a", default=True)], min_values=0, max_values=1)
    handle_message_parameter(components=[valid])
    invalid = interaction.Selection("pick", [interaction.SelectOption("A", "a")], min_values=2, max_values=1)
    with pytest.raises(ValueError, match="min_values/max_values"):
        handle_message_parameter(components=[invalid])


def test_string_select_rejects_empty_options_and_disabled_modal():
    with pytest.raises(ValueError, match="1 to 25"):
        handle_message_parameter(components=[interaction.Selection("pick", [])])
    select = interaction.Selection("pick", [interaction.SelectOption("A", "a")], disabled=True)
    with pytest.raises(ValueError, match="disabled"):
        validate_modal_components([interaction.Label(select, label="Pick")])


def test_string_select_defaults_cannot_exceed_max_values():
    select = interaction.Selection(
        "pick", [
            interaction.SelectOption("A", "a", default=True),
            interaction.SelectOption("B", "b", default=True),
        ], max_values=1,
    )
    with pytest.raises(ValueError, match="defaults"):
        handle_message_parameter(components=[select])


def test_modal_string_select_submission_preserves_values(offline_client, user_payload):
    payload = {
        "id": "40", "application_id": "20", "type": 5, "token": "tk",
        "version": 1, "user": user_payload, "channel_id": "30",
        "data": {
            "custom_id": "survey",
            "components": [{
                "type": 18,
                "component": {"type": 3, "custom_id": "pet", "values": ["cat"]},
            }],
        },
    }
    context = interaction.ModalSubmitContext(payload, offline_client)
    assert context.components[0].values == ["cat"]
    assert "values" not in context.components[0].to_dict()
