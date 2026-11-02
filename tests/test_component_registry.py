"""Known component type numbers select their registered payload parser."""

import pytest

from discord.ext.interaction.component_models import Component
from discord.ext.interaction.component_codec import ComponentRegistry


class Display(Component):
    TYPE = 10

    def __init__(self, content: str, *, id: int | None = None):
        super().__init__(id=id)
        self.content = content

    def to_payload(self):
        return {**self._base_payload(), "content": self.content}

    @classmethod
    def from_payload(cls, payload):
        return cls(payload["content"], id=payload.get("id"))


class DuplicateDisplay(Display):
    TYPE = 10


def test_registered_type_round_trips_through_parser():
    registry = ComponentRegistry()
    registry.register(Display)
    registry.register(Display)
    payload = {"type": 10, "id": 7, "content": "hello"}

    parsed = registry.from_payload(payload)
    assert isinstance(parsed, Display)
    assert parsed.to_payload() == payload


def test_registration_rejects_type_conflicts_and_invalid_models():
    registry = ComponentRegistry()
    registry.register(Display)
    with pytest.raises(ValueError, match="already registered"):
        registry.register(DuplicateDisplay)
    with pytest.raises(TypeError, match="inherit Component"):
        registry.register(object)
    with pytest.raises(TypeError, match="payload methods"):
        registry.register(Component)
