"""Create and submit a mixed Discord modal with all newly supported inputs."""

import pytest

from discord.ext import interaction
from discord.ext.interaction.implementation.component_validation import validate_modal_components
from discord.ext.interaction.implementation.components import from_payload


def test_mixed_modal_inputs_round_trip(offline_client, user_payload):
    inputs = [
        interaction.Label(interaction.TextInput("note", 1), label="Note"),
        interaction.Label(interaction.FileUpload("files"), label="Files"),
        interaction.Label(interaction.RadioGroup("choice", [
            interaction.RadioGroupOption("a", "A"),
            interaction.RadioGroupOption("b", "B"),
        ]), label="Choice"),
        interaction.Label(interaction.CheckboxGroup("checks", [
            interaction.CheckboxGroupOption("a", "A"),
        ]), label="Checks"),
        interaction.Label(interaction.Checkbox("accept"), label="Accept"),
    ]
    validate_modal_components(inputs)
    created = [item.to_all_dict() for item in inputs]
    assert [item.component.TYPE for item in from_payload(created)] == [4, 19, 21, 22, 23]

    received = [
        {"type": 18, "component": {"type": 4, "custom_id": "note", "value": "hello"}},
        {"type": 18, "component": {"type": 19, "custom_id": "files", "values": []}},
        {"type": 18, "component": {"type": 21, "custom_id": "choice", "value": "b"}},
        {"type": 18, "component": {"type": 22, "custom_id": "checks", "values": ["a"]}},
        {"type": 18, "component": {"type": 23, "custom_id": "accept", "value": False}},
    ]
    payload = {
        "id": "40", "application_id": "20", "type": 5, "token": "tk",
        "version": 1, "user": user_payload, "channel_id": "30",
        "data": {"custom_id": "survey", "components": received},
    }
    context = interaction.ModalSubmitContext(payload, offline_client)
    assert context.get_component("note").value == "hello"
    assert context.get_component("files").values == []
    assert context.get_component("choice").value == "b"
    assert context.get_component("checks").values == ["a"]
    assert context.get_component("accept").value is False


def test_mixed_modal_rejects_duplicate_ids_and_more_than_five_inputs():
    labels = [interaction.Label(interaction.Checkbox("same"), label="One")]
    with pytest.raises(ValueError, match="duplicate"):
        validate_modal_components(labels * 2)
    with pytest.raises(ValueError, match="1 to 5"):
        validate_modal_components([
            interaction.Label(interaction.Checkbox(str(index)), label="Choice")
            for index in range(6)
        ])
