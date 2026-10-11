"""Base class for the existing Components API."""

from abc import ABCMeta, abstractmethod

import discord


class Components(metaclass=ABCMeta):
    TYPE: int | None = None

    def __init__(self, components_type: discord.ComponentType):
        self.type = components_type

    @abstractmethod
    def to_dict(self) -> dict:
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, payload: dict) -> dict:
        pass

    def __eq__(self, other):
        return self.type == other.type

    def __ne__(self, other):
        return not self.__eq__(other)
