"""The existing modal TextInput API."""

import discord

from discord.ext.interaction.models.legacy_base import Components


class TextInput(Components):
    """Represents an interactive text input rendered on a modal."""

    TYPE = 4

    def __init__(
        self,
        custom_id: str,
        style: int,
        label: str | None = None,
        min_length: int | None = None,
        max_length: int | None = None,
        required: bool = False,
        value: str | None = None,
        placeholder: str | None = None,
    ):
        super().__init__(components_type=discord.ComponentType.text_input)

        self.custom_id = custom_id
        self.style = style
        self.label = label
        self.placeholder = placeholder
        self.min_length = min_length
        self.max_length = max_length
        self.required = required
        self.value = value

    def __eq__(self, other):
        return self.custom_id == other.custom_id and super().__eq__(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def to_dict(self) -> dict:
        base = {
            "type": 4,
            "custom_id": self.custom_id,
            "style": self.style,
            "required": self.required,
        }
        if self.label is not None:
            base["label"] = self.label
        if self.placeholder is not None:
            base["placeholder"] = self.placeholder
        if self.min_length is not None:
            base["min_length"] = self.min_length
        if self.max_length is not None:
            base["max_length"] = self.max_length
        if self.value is not None:
            base["value"] = self.value

        return base

    @classmethod
    def from_dict(cls, payload: dict):
        custom_id = payload["custom_id"]
        style = payload.get("style")
        label = payload.get("label")
        placeholder = payload.get("placeholder")
        min_length = payload.get("min_length")
        max_length = payload.get("max_length")
        required = payload.get("required", False)
        value = payload.get("value")
        return cls(
            custom_id=custom_id,
            style=style,
            label=label,
            placeholder=placeholder,
            min_length=min_length,
            max_length=max_length,
            required=required,
            value=value,
        )
