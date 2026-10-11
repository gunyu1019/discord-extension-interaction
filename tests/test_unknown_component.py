"""Unknown Discord component fields survive parsing and serialization."""

import pytest

from discord.ext.interaction.models.unknown_component import UnknownComponent
from discord.ext.interaction.models.component_codec import ComponentRegistry


def test_unknown_component_preserves_future_fields_without_aliasing_input():
    payload = {
        "type": 99,
        "id": 42,
        "content": "future component",
        "extra": {"items": [{"value": 1}]},
    }
    component = ComponentRegistry().from_payload(payload)
    payload["extra"]["items"][0]["value"] = 2

    assert isinstance(component, UnknownComponent)
    assert component.type == 99
    assert component.id == 42
    assert component.to_payload()["extra"] == {"items": [{"value": 1}]}

    returned = component.raw_payload
    returned["extra"]["items"].append({"value": 3})
    assert component.to_payload()["extra"] == {"items": [{"value": 1}]}


def test_unknown_component_rejects_malformed_type_and_id():
    with pytest.raises(ValueError):
        UnknownComponent({"type": "99"})
    with pytest.raises(ValueError):
        UnknownComponent({"type": 99, "id": -1})
