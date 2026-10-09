"""The existing String Select option API."""

import discord


class SelectOption:
    """Represents a select menu's option."""

    def __init__(
        self,
        label: str,
        value: str,
        description: str | None = None,
        emoji: discord.PartialEmoji | dict = None,
        default: bool = False,
    ):
        self.label = label
        self.value = value
        self.description = description
        self.emoji = emoji
        self.default = default

    def __str__(self) -> str:
        if self.emoji:
            base = f"{self.emoji} {self.label}"
        else:
            base = self.label

        if self.description:
            return f"{base}\n{self.description}"
        return base

    def __eq__(self, other):
        return self.value == other.value

    def __ne__(self, other):
        return not self.__eq__(other)

    def to_dict(self) -> dict:
        data = {"label": self.label, "value": self.value}

        if self.description is not None:
            data["description"] = self.description
        if self.emoji is not None:
            data["emoji"] = (
                self.emoji.to_dict()
                if isinstance(self.emoji, discord.PartialEmoji)
                else self.emoji
            )
        if self.default is not None:
            data["default"] = self.default

        return data

    @classmethod
    def from_dict(cls, payload: dict):
        label: str = payload.get("label")
        value: str = payload.get("value")
        description: str | None = payload.get("description")
        emoji: discord.PartialEmoji = payload.get("emoji")
        default: bool = payload.get("default", False)
        return cls(
            label=label,
            value=value,
            description=description,
            emoji=emoji,
            default=default,
        )
