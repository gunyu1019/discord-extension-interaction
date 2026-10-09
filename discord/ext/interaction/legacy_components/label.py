"""The existing modal Label model."""

import discord

from .base import Components


class Label(Components):
    """A modal-only container around one interactive component."""

    TYPE = 18

    def __init__(
        self,
        component: Components,
        label: str | None = None,
        description: str | None = None,
    ):
        super().__init__(components_type=discord.ComponentType.label)
        self.label = label
        self.description = description
        self.component = component

    @property
    def components(self) -> list:
        """Expose the wrapped child with the ActionRow list shape."""
        return [self.component] if self.component is not None else []

    def to_dict(self) -> dict:
        base = {"type": 18, "component": self.component}
        if self.label is not None:
            base["label"] = self.label
        if self.description is not None:
            base["description"] = self.description
        return base

    def to_all_dict(self) -> dict:
        base = self.to_dict()
        child = self.component.to_dict()
        # The Label carries the label/description; Discord rejects them on the child.
        child.pop("label", None)
        child.pop("description", None)
        base["component"] = child
        return base

    @classmethod
    def from_dict(cls, payload: dict):
        return cls(
            component=payload.get("component"),
            label=payload.get("label"),
            description=payload.get("description"),
        )

    @classmethod
    def from_payload(cls, payload: dict):
        # The facade parser is retained until the remaining legacy models move.
        from ..components import from_payload

        child = from_payload([payload["component"]]) if payload.get("component") else []
        return cls(
            component=child[0] if child else None,
            label=payload.get("label"),
            description=payload.get("description"),
        )

    def __eq__(self, other):
        return (
            self.component == other.component
            and self.label == other.label
            and super().__eq__(other)
        )

    def __ne__(self, other):
        return not self.__eq__(other)
