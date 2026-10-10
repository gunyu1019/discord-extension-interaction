"""Discord Checkbox modal input."""

from typing import Any

from .component import Component


class Checkbox(Component):
    """A modal yes/no input whose submission carries a boolean value."""

    TYPE = 23

    def __init__(
        self,
        custom_id: str,
        *,
        default: bool | None = None,
        value: bool | None = None,
        id: int | None = None,
    ):
        super().__init__(id=id)
        if not isinstance(custom_id, str) or not 1 <= len(custom_id) <= 100:
            raise ValueError("Checkbox custom_id requires 1 to 100 characters")
        if default is not None and type(default) is not bool:
            raise ValueError("Checkbox default must be a boolean")
        if value is not None and type(value) is not bool:
            raise ValueError("Checkbox value must be a boolean")
        self.custom_id = custom_id
        self.default = default
        self.value = value

    def to_payload(self) -> dict[str, Any]:
        payload = {**self._base_payload(), "custom_id": self.custom_id}
        if self.default is not None:
            payload["default"] = self.default
        return payload

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "Checkbox":
        return cls(
            payload["custom_id"],
            default=payload.get("default"),
            value=payload.get("value"),
            id=payload.get("id"),
        )
