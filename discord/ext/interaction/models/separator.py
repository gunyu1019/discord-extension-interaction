"""Discord Separator component."""

from typing import Any

from discord.ext.interaction.models.component import Component


class Separator(Component):
    """Spacing or a divider in a Components V2 message."""

    TYPE = 14

    def __init__(
        self, *, divider: bool = True, spacing: int = 1, id: int | None = None
    ):
        super().__init__(id=id)
        if type(divider) is not bool:
            raise ValueError("Separator divider must be a boolean")
        if type(spacing) is not int or spacing not in (1, 2):
            raise ValueError("Separator spacing must be 1 or 2")
        self.divider = divider
        self.spacing = spacing

    def to_payload(self) -> dict[str, Any]:
        return {
            **self._base_payload(),
            "divider": self.divider,
            "spacing": self.spacing,
        }

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "Separator":
        return cls(
            divider=payload.get("divider", True),
            spacing=payload.get("spacing", 1),
            id=payload.get("id"),
        )
