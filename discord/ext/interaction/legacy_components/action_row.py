"""The existing ActionRow layout model."""

import discord

from .base import Components


class ActionRow(Components):
    """A non-interactive row containing existing component objects."""

    TYPE = 1

    def __init__(self, components: list[Components] = None):
        super().__init__(components_type=discord.ComponentType.action_row)
        self.components: list = components

    def to_dict(self) -> dict:
        return {"type": 1, "components": self.components}

    def to_all_dict(self) -> dict:
        return {"type": 1, "components": [i.to_dict() for i in self.components]}

    @classmethod
    def from_dict(cls, payload: dict):
        components = payload.get("components")
        return cls(components=components)

    @classmethod
    def from_payload(cls, payload: dict):
        from .parsing import from_payload

        components = from_payload(payload.get("components"))
        return cls(components=components)

    def __eq__(self, other):
        return self.components == other.components and super().__eq__(other)

    def __ne__(self, other):
        return not self.__eq__(other)
