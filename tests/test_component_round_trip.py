"""Legacy and future component payloads survive receive and serialize cycles."""

from discord.ext.interaction.implementation.components import ActionRow, Label, from_payload
from discord.ext.interaction.models.unknown_component import UnknownComponent


def test_known_action_row_and_label_round_trip():
    source = [
        {"type": 1, "components": [{"type": 2, "style": 1, "label": "Go", "custom_id": "go"}]},
        {"type": 18, "label": "Name", "component": {"type": 4, "style": 1, "custom_id": "name"}},
    ]
    row, label = from_payload(source)
    assert isinstance(row, ActionRow)
    assert isinstance(label, Label)
    assert row.to_all_dict() == {
        "type": 1,
        "components": [{**source[0]["components"][0], "disabled": False}],
    }
    assert label.to_all_dict() == {**source[1], "component": {**source[1]["component"], "required": False}}


def test_unknown_top_level_and_nested_components_preserve_payload():
    source = [
        {"type": 99, "id": 3, "new_field": {"nested": [1, 2]}},
        {"type": 1, "components": [{"type": 100, "custom_id": "future", "value": True}]},
    ]
    unknown, row = from_payload(source)
    assert isinstance(unknown, UnknownComponent)
    assert unknown.to_payload() == source[0]
    assert row.to_all_dict() == source[1]
