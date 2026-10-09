"""Forward-compatible component model for Discord types not yet implemented."""

from copy import deepcopy
from typing import Any

from .component import Component


class UnknownComponent(Component):
    """Preserve every payload field of an unrecognized component type."""

    def __init__(self, payload: dict[str, Any]):
        component_type = payload["type"]
        if type(component_type) is not int or component_type <= 0:
            raise ValueError("component type must be a positive integer")
        super().__init__(id=payload.get("id"))
        self.TYPE = component_type
        self._payload = deepcopy(payload)

    @property
    def raw_payload(self) -> dict[str, Any]:
        return deepcopy(self._payload)

    def to_payload(self) -> dict[str, Any]:
        return deepcopy(self._payload)

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "UnknownComponent":
        return cls(payload)
