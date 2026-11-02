"""The existing Button API."""

import discord

from discord.ext.interaction.enums import get_enum
from discord.ext.interaction.models.legacy_base import Components


class Button(Components):
    """Represents a Button with style, label, emoji and an action target."""

    TYPE = 2

    def __init__(
        self,
        style: int | discord.ButtonStyle,
        label: str = None,
        emoji: discord.PartialEmoji | str | dict = None,
        custom_id: str = None,
        url: str = None,
        disabled: bool = None,
        sku_id: int | str = None,
    ):
        super().__init__(components_type=discord.ComponentType.button)

        # Accepting a button's style as an int will be disabled.
        if isinstance(style, int):
            style = get_enum(discord.ButtonStyle, style)
        self.style = style
        self.label = label
        self.emoji = emoji
        self.custom_id = custom_id
        self.url = url
        self.sku_id = sku_id
        self.disabled = disabled

    def to_dict(self) -> dict:
        base = {"type": 2, "style": int(self.style)}

        if self.label is not None:
            base["label"] = self.label
        if self.emoji is not None and isinstance(self.emoji, discord.PartialEmoji):
            base["emoji"] = self.emoji.to_dict()
        elif self.emoji is not None and isinstance(self.emoji, str):
            base["emoji"] = {"name": self.emoji}
        elif self.emoji is not None:
            base["emoji"] = self.emoji

        if 0 < int(self.style) < 5 and self.custom_id is not None:
            base["custom_id"] = self.custom_id
        if int(self.style) == 5 and self.url is not None:
            base["url"] = self.url
        if int(self.style) == 6 and self.sku_id is not None:
            base["sku_id"] = str(self.sku_id)

        if self.disabled is not None:
            base["disabled"] = self.disabled

        return base

    @classmethod
    def from_dict(cls, payload: dict):
        style = get_enum(discord.ButtonStyle, payload["style"])
        label = payload.get("label")
        emoji = payload.get("emoji")
        custom_id = payload.get("custom_id")
        url = payload.get("url")
        sku_id = payload.get("sku_id")
        disabled = payload.get("disabled", False)
        return cls(
            style=style,
            label=label,
            emoji=emoji,
            custom_id=custom_id,
            url=url,
            sku_id=sku_id,
            disabled=disabled,
        )

    def __eq__(self, other):
        return self.custom_id == other.custom_id and super().__eq__(other)

    def __ne__(self, other):
        return not self.__eq__(other)
