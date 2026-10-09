"""Discord Section layout component."""

from typing import Any

from .component import Component
from .text_display import TextDisplay
from .thumbnail import Thumbnail
from .unknown_component import UnknownComponent


class Section(Component):
    """One to three text components beside an accessory."""

    TYPE = 9

    def __init__(
        self,
        components: list[Component],
        accessory: Component,
        *,
        id: int | None = None,
    ):
        super().__init__(id=id)
        if not 1 <= len(components) <= 3:
            raise ValueError("Section requires 1 to 3 child components")
        if not all(isinstance(item, Component) for item in components):
            raise TypeError("Section children must be component models")
        if not isinstance(accessory, Component):
            raise TypeError("Section accessory must be a component model")
        self.components = list(components)
        self.accessory = accessory

    def to_payload(self) -> dict[str, Any]:
        return {
            **self._base_payload(),
            "components": [item.to_payload() for item in self.components],
            "accessory": self.accessory.to_payload(),
        }

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "Section":
        children = [
            TextDisplay.from_payload(item) if item["type"] == 10
            else UnknownComponent.from_payload(item)
            for item in payload["components"]
        ]
        return cls(
            children,
            (
                Thumbnail.from_payload(payload["accessory"])
                if payload["accessory"]["type"] == 11
                else UnknownComponent.from_payload(payload["accessory"])
            ),
            id=payload.get("id"),
        )
