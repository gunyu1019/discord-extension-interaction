"""The existing String Select model, publicly named Selection."""

import discord

from .base import Components
from .select_option import SelectOption


class Selection(Components):
    """Represents a Select Menu."""

    TYPE = 3

    def __init__(
        self,
        custom_id: str,
        options: list[dict | SelectOption],
        disabled: bool = False,
        placeholder: str = None,
        min_values: int = None,
        max_values: int = None,
    ):
        super().__init__(components_type=discord.ComponentType.select)

        self.disabled = disabled
        self.custom_id = custom_id
        self.options = options
        self.placeholder = placeholder
        self.min_values = min_values
        self.max_values = max_values

    def to_dict(self) -> dict:
        base = {
            "type": 3,
            "custom_id": self.custom_id,
            "disabled": self.disabled,
            "options": [
                option.to_dict() if isinstance(option, SelectOption) else option
                for option in self.options
            ],
        }
        if self.placeholder is not None:
            base["placeholder"] = self.placeholder
        if self.min_values is not None:
            base["min_values"] = self.min_values
        if self.max_values is not None:
            base["max_values"] = self.max_values

        return base

    def __eq__(self, other):
        return (
            self.custom_id == other.custom_id
            and super().__eq__(other)
            and self.options == other.options
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    @classmethod
    def from_dict(cls, payload: dict):
        custom_id = payload["custom_id"]
        options = [SelectOption.from_dict(x) for x in payload.get("options", [])]
        placeholder = payload.get("placeholder")
        min_values = payload.get("min_values")
        max_values = payload.get("max_values")
        return cls(
            custom_id=custom_id,
            options=options,
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
        )
