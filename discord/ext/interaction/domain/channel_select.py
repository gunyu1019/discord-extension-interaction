"""Discord Channel Select component."""

from typing import Any

from .auto_select import AutoSelect
from .select_default_value import SelectDefaultValue


class ChannelSelect(AutoSelect):
    TYPE = 8
    DEFAULT_TYPES = ("channel",)

    def __init__(
        self, custom_id: str, *, channel_types: list[int] | None = None, **kwargs
    ):
        super().__init__(custom_id, **kwargs)
        normalized = [getattr(value, "value", value) for value in channel_types or ()]
        if channel_types is not None and not all(
            type(value) is int and value >= 0 for value in normalized
        ):
            raise ValueError("Channel Select channel_types must be nonnegative integers")
        self.channel_types = normalized if channel_types is not None else None

    def to_payload(self) -> dict[str, Any]:
        payload = super().to_payload()
        if self.channel_types is not None:
            payload["channel_types"] = list(self.channel_types)
        return payload

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "ChannelSelect":
        return cls(
            payload["custom_id"],
            channel_types=payload.get("channel_types"),
            placeholder=payload.get("placeholder"),
            min_values=payload.get("min_values"),
            max_values=payload.get("max_values"),
            required=payload.get("required"),
            disabled=payload.get("disabled"),
            default_values=(
                [SelectDefaultValue.from_payload(item) for item in payload["default_values"]]
                if "default_values" in payload else None
            ),
            values=payload.get("values"),
            id=payload.get("id"),
        )
