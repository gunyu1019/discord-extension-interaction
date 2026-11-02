"""Checkbox creation and submission use distinct default and value fields."""

import pytest

from discord.ext import interaction
from discord.ext.interaction.components import from_payload
from discord.ext.interaction.component_validation import validate_modal_components


def test_checkbox_modal_and_submission_round_trip():
    checkbox = interaction.Checkbox("accept", default=False)
    label = interaction.Label(checkbox, label="Accept terms")
    validate_modal_components([label])
    payload = label.to_all_dict()
    assert payload["component"] == {"type": 23, "custom_id": "accept", "default": False}
    assert isinstance(from_payload([payload])[0].component, interaction.Checkbox)

    submitted = from_payload([{"type": 18, "component": {
        "type": 23, "custom_id": "accept", "value": False,
    }}])[0].component
    assert submitted.value is False
    assert "value" not in submitted.to_payload()


@pytest.mark.parametrize("field", ["default", "value"])
def test_checkbox_rejects_non_boolean(field):
    with pytest.raises(ValueError, match="boolean"):
        interaction.Checkbox("accept", **{field: 1})
