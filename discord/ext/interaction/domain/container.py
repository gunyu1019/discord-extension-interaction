"""Discord Container layout component."""

from typing import Any

from .component import Component
from .section import Section
from .media_gallery import MediaGallery
from .separator import Separator
from .text_display import TextDisplay
from .unknown_component import UnknownComponent


_KNOWN_CHILDREN = {
    Section.TYPE: Section,
    TextDisplay.TYPE: TextDisplay,
    Separator.TYPE: Separator,
    MediaGallery.TYPE: MediaGallery,
}


class Container(Component):
    """Visual grouping of Components V2 message content."""

    TYPE = 17

    def __init__(
        self,
        components: list[Component],
        *,
        accent_color: int | None = None,
        spoiler: bool = False,
        id: int | None = None,
    ):
        super().__init__(id=id)
        if not components or not all(isinstance(item, Component) for item in components):
            raise ValueError("Container requires component model children")
        if accent_color is not None and (
            type(accent_color) is not int or not 0 <= accent_color <= 0xFFFFFF
        ):
            raise ValueError("Container accent_color must be an RGB integer")
        if type(spoiler) is not bool:
            raise ValueError("Container spoiler must be a boolean")
        self.components = list(components)
        self.accent_color = accent_color
        self.spoiler = spoiler

    def to_payload(self) -> dict[str, Any]:
        payload = {
            **self._base_payload(),
            "components": [item.to_payload() for item in self.components],
            "spoiler": self.spoiler,
        }
        if self.accent_color is not None:
            payload["accent_color"] = self.accent_color
        return payload

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "Container":
        children = [
            _KNOWN_CHILDREN.get(item["type"], UnknownComponent).from_payload(item)
            for item in payload["components"]
        ]
        return cls(
            children,
            accent_color=payload.get("accent_color"),
            spoiler=payload.get("spoiler", False),
            id=payload.get("id"),
        )
