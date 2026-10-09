"""Discord Text Display component."""

from typing import Any

from .component import Component


class TextDisplay(Component):
    """Markdown text for a Components V2 message or a modal."""

    TYPE = 10

    def __init__(self, content: str, *, id: int | None = None):
        super().__init__(id=id)
        if not isinstance(content, str) or not content:
            raise ValueError("Text Display content must be a nonempty string")
        self.content = content

    def to_payload(self) -> dict[str, Any]:
        return {**self._base_payload(), "content": self.content}

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "TextDisplay":
        return cls(payload["content"], id=payload.get("id"))
