"""Discord auto-select default value object."""

from typing import Any


class SelectDefaultValue:
    """A user, role, or channel selected when a menu first appears."""

    def __init__(self, id: int | str, type: str):
        if type not in ("user", "role", "channel"):
            raise ValueError("default value type must be user, role, or channel")
        if not str(id).isdigit() or int(id) <= 0:
            raise ValueError("default value id must be a snowflake")
        self.id = str(id)
        self.type = type

    def to_payload(self) -> dict[str, Any]:
        return {"id": self.id, "type": self.type}

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "SelectDefaultValue":
        return cls(payload["id"], payload["type"])
