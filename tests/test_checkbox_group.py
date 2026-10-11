"""Checkbox Group validates bounds and retains submitted values."""

import pytest

from discord.ext import interaction
from discord.ext.interaction.implementation.components import from_payload


def test_checkbox_group_modal_and_submission_round_trip():
    group = interaction.CheckboxGroup(
        "days", [
            interaction.CheckboxGroupOption("mon", "Monday", default=True),
            interaction.CheckboxGroupOption("tue", "Tuesday"),
        ], min_values=0, max_values=2, required=False,
    )
    payload = interaction.Label(group, label="Days").to_all_dict()
    assert payload["component"]["options"][0]["default"] is True
    assert isinstance(from_payload([payload])[0].component, interaction.CheckboxGroup)
    submitted = from_payload([{"type": 18, "component": {
        "type": 22, "custom_id": "days", "values": ["mon", "tue"],
    }}])[0]
    assert submitted.component.values == ["mon", "tue"]


def test_checkbox_group_rejects_bad_bounds():
    options = [interaction.CheckboxGroupOption("mon", "Monday")]
    with pytest.raises(ValueError, match="min_values/max_values"):
        interaction.CheckboxGroup("days", options, min_values=2)
