"""Shared Discord auto-populated select menu fields."""

from typing import Any

from .component import Component
from .select_default_value import SelectDefaultValue


class AutoSelect(Component):
    """Common fields for User, Role, Mentionable and Channel Selects."""

    DEFAULT_TYPES: tuple[str, ...] = ()

    def __init__(
        self,
        custom_id: str,
        *,
        placeholder: str | None = None,
        min_values: int | None = None,
        max_values: int | None = None,
        required: bool | None = None,
        disabled: bool | None = None,
        default_values: list[SelectDefaultValue] | None = None,
        values: list[str] | None = None,
        id: int | None = None,
    ):
        super().__init__(id=id)
        if not isinstance(custom_id, str) or not 1 <= len(custom_id) <= 100:
            raise ValueError("select custom_id requires 1 to 100 characters")
        if placeholder is not None and (
            not isinstance(placeholder, str) or len(placeholder) > 150
        ):
            raise ValueError("select placeholder exceeds 150 characters")
        minimum = 1 if min_values is None else min_values
        maximum = 1 if max_values is None else max_values
        if (
            type(minimum) is not int
            or type(maximum) is not int
            or not 0 <= minimum <= maximum <= 25
        ):
            raise ValueError("select min_values/max_values are invalid")
        if required is not None and type(required) is not bool:
            raise ValueError("select required must be a boolean")
        if disabled is not None and type(disabled) is not bool:
            raise ValueError("select disabled must be a boolean")
        if default_values is not None:
            if not all(isinstance(item, SelectDefaultValue) for item in default_values):
                raise TypeError(
                    "select default_values require SelectDefaultValue objects"
                )
            if not minimum <= len(default_values) <= maximum:
                raise ValueError(
                    "select default_values count is outside min_values/max_values"
                )
            if any(item.type not in self.DEFAULT_TYPES for item in default_values):
                raise ValueError(
                    "select default_values type is not allowed for this menu"
                )
        self.custom_id = custom_id
        self.placeholder = placeholder
        self.min_values = min_values
        self.max_values = max_values
        self.required = required
        self.disabled = disabled
        self.default_values = (
            list(default_values) if default_values is not None else None
        )
        self.values = list(values) if values is not None else []

    def to_payload(self) -> dict[str, Any]:
        payload = {**self._base_payload(), "custom_id": self.custom_id}
        for key in ("placeholder", "min_values", "max_values", "required", "disabled"):
            value = getattr(self, key)
            if value is not None:
                payload[key] = value
        if self.default_values is not None:
            payload["default_values"] = [
                item.to_payload() for item in self.default_values
            ]
        return payload

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "AutoSelect":
        return cls(
            payload["custom_id"],
            placeholder=payload.get("placeholder"),
            min_values=payload.get("min_values"),
            max_values=payload.get("max_values"),
            required=payload.get("required"),
            disabled=payload.get("disabled"),
            default_values=(
                [
                    SelectDefaultValue.from_payload(item)
                    for item in payload["default_values"]
                ]
                if "default_values" in payload
                else None
            ),
            values=payload.get("values"),
            id=payload.get("id"),
        )
