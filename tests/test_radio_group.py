"""Radio Group options and submitted value follow Discord modal payloads."""

import pytest

from discord.ext import interaction
from discord.ext.interaction.implementation.components import from_payload
from discord.ext.interaction.implementation.component_validation import validate_modal_components


def test_radio_group_modal_and_submission_round_trip():
    radio = interaction.RadioGroup(
        "class", [
            interaction.RadioGroupOption("mage", "Mage", default=True),
            interaction.RadioGroupOption("warrior", "Warrior"),
        ]
    )
    payload = interaction.Label(radio, label="Class").to_all_dict()
    assert payload["component"]["options"][0]["default"] is True
    assert isinstance(from_payload([payload])[0].component, interaction.RadioGroup)
    submitted = from_payload([{"type": 18, "component": {
        "type": 21, "custom_id": "class", "value": "warrior",
    }}])[0]
    assert submitted.component.value == "warrior"


def test_radio_group_rejects_multiple_defaults_and_missing_options():
    options = [interaction.RadioGroupOption(str(i), str(i), default=True) for i in range(2)]
    with pytest.raises(ValueError, match="at most one default"):
        interaction.RadioGroup("class", options)
    with pytest.raises(ValueError, match="requires options"):
        validate_modal_components([interaction.Label(interaction.RadioGroup("class"), label="Class")])
