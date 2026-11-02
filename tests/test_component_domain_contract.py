"""New component models use Discord's shared type and optional numeric id."""

import pytest

from discord.ext.interaction.models.components import Component


class ExampleComponent(Component):
    TYPE = 10

    def __init__(self, content: str, *, id: int | None = None):
        super().__init__(id=id)
        self.content = content

    def to_payload(self):
        return {**self._base_payload(), "content": self.content}

    @classmethod
    def from_payload(cls, payload):
        return cls(payload["content"], id=payload.get("id"))


def test_component_contract_round_trips_optional_id():
    component = ExampleComponent("hello", id=0)
    payload = component.to_payload()
    assert payload == {"type": 10, "id": 0, "content": "hello"}
    assert ExampleComponent.from_payload(payload).to_payload() == payload
    assert ExampleComponent("hello").to_payload() == {
        "type": 10, "content": "hello",
    }


@pytest.mark.parametrize("component_id", [-1, 0x100000000, True, "1"])
def test_component_id_rejects_values_outside_discord_contract(component_id):
    with pytest.raises(ValueError):
        ExampleComponent("hello", id=component_id)


def test_component_contract_requires_payload_methods():
    with pytest.raises(TypeError):
        Component()
