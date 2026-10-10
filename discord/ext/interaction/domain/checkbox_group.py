"""Discord Checkbox Group modal input."""

from typing import Any

from .choice_group_option import ChoiceGroupOption
from .component import Component


class CheckboxGroupOption(ChoiceGroupOption):
    """One Checkbox Group choice."""


class CheckboxGroup(Component):
    """A modal input that returns zero or more selected values."""

    TYPE = 22

    def __init__(
        self,
        custom_id: str,
        options: list[CheckboxGroupOption] | None = None,
        *,
        min_values: int | None = None,
        max_values: int | None = None,
        required: bool = True,
        values: list[str] | None = None,
        id: int | None = None,
    ):
        super().__init__(id=id)
        if not isinstance(custom_id, str) or not 1 <= len(custom_id) <= 100:
            raise ValueError("Checkbox Group custom_id requires 1 to 100 characters")
        if options is not None and (
            not 1 <= len(options) <= 10
            or not all(isinstance(option, CheckboxGroupOption) for option in options)
        ):
            raise ValueError("Checkbox Group requires 1 to 10 options")
        if type(required) is not bool:
            raise ValueError("Checkbox Group required must be a boolean")
        minimum = 1 if min_values is None else min_values
        maximum = (len(options) if options is not None else 10) if max_values is None else max_values
        if (type(minimum) is not int or type(maximum) is not int
                or not 0 <= minimum <= maximum <= 10
                or options is not None and maximum > len(options)
                or required and minimum == 0):
            raise ValueError("Checkbox Group min_values/max_values are invalid")
        if options is not None and sum(option.default is True for option in options) > maximum:
            raise ValueError("Checkbox Group defaults exceed max_values")
        self.custom_id = custom_id
        self.options = list(options) if options is not None else None
        self.min_values = min_values
        self.max_values = max_values
        self.required = required
        self.values = list(values) if values is not None else []

    def to_payload(self) -> dict[str, Any]:
        payload = {**self._base_payload(), "custom_id": self.custom_id}
        if self.options is not None:
            payload["options"] = [option.to_payload() for option in self.options]
            if self.min_values is not None:
                payload["min_values"] = self.min_values
            if self.max_values is not None:
                payload["max_values"] = self.max_values
            payload["required"] = self.required
        return payload

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "CheckboxGroup":
        return cls(
            payload["custom_id"],
            options=(
                [CheckboxGroupOption.from_payload(option) for option in payload["options"]]
                if "options" in payload else None
            ),
            min_values=payload.get("min_values"),
            max_values=payload.get("max_values"),
            required=payload.get("required", True),
            values=payload.get("values"),
            id=payload.get("id"),
        )
