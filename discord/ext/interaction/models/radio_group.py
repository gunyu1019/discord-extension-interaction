"""Discord Radio Group modal input."""

from typing import Any

from discord.ext.interaction.models.choice_group_option import ChoiceGroupOption
from discord.ext.interaction.models.component import Component


class RadioGroupOption(ChoiceGroupOption):
    """One Radio Group choice."""


class RadioGroup(Component):
    """A modal input that returns one selected option value."""

    TYPE = 21

    def __init__(
        self,
        custom_id: str,
        options: list[RadioGroupOption] | None = None,
        *,
        required: bool = True,
        value: str | None = None,
        id: int | None = None,
    ):
        super().__init__(id=id)
        if not isinstance(custom_id, str) or not 1 <= len(custom_id) <= 100:
            raise ValueError("Radio Group custom_id requires 1 to 100 characters")
        if options is not None and (
            not 2 <= len(options) <= 10
            or not all(isinstance(option, RadioGroupOption) for option in options)
            or sum(option.default is True for option in options) > 1
        ):
            raise ValueError(
                "Radio Group requires 2 to 10 options and at most one default"
            )
        if type(required) is not bool:
            raise ValueError("Radio Group required must be a boolean")
        self.custom_id = custom_id
        self.options = list(options) if options is not None else None
        self.required = required
        self.value = value

    def to_payload(self) -> dict[str, Any]:
        payload = {**self._base_payload(), "custom_id": self.custom_id}
        if self.options is not None:
            payload["options"] = [option.to_payload() for option in self.options]
            payload["required"] = self.required
        return payload

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "RadioGroup":
        return cls(
            payload["custom_id"],
            options=(
                [RadioGroupOption.from_payload(option) for option in payload["options"]]
                if "options" in payload
                else None
            ),
            required=payload.get("required", True),
            value=payload.get("value"),
            id=payload.get("id"),
        )
