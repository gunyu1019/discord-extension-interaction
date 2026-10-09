"""Shared option fields for Discord Radio and Checkbox Groups."""

from typing import Any


class ChoiceGroupOption:
    """Value, label, optional description and default selection."""

    def __init__(
        self, value: str, label: str, *, description: str | None = None,
        default: bool | None = None,
    ):
        if not isinstance(value, str) or not 1 <= len(value) <= 100:
            raise ValueError("choice option value requires 1 to 100 characters")
        if not isinstance(label, str) or not 1 <= len(label) <= 100:
            raise ValueError("choice option label requires 1 to 100 characters")
        if description is not None and (
            not isinstance(description, str) or len(description) > 100
        ):
            raise ValueError("choice option description exceeds 100 characters")
        if default is not None and type(default) is not bool:
            raise ValueError("choice option default must be a boolean")
        self.value = value
        self.label = label
        self.description = description
        self.default = default

    def to_payload(self) -> dict[str, Any]:
        payload = {"value": self.value, "label": self.label}
        if self.description is not None:
            payload["description"] = self.description
        if self.default is not None:
            payload["default"] = self.default
        return payload

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "ChoiceGroupOption":
        return cls(
            payload["value"], payload["label"],
            description=payload.get("description"), default=payload.get("default"),
        )
