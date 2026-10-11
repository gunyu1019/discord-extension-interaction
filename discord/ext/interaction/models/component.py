"""Shared Discord Component Object contract for new component models."""

from abc import ABC, abstractmethod
from typing import Any, ClassVar


class Component(ABC):
    """A component with Discord's ``type`` and optional 32-bit ``id`` fields."""

    TYPE: ClassVar[int]

    def __init__(self, *, id: int | None = None):
        if id is not None and (type(id) is not int or not 0 <= id <= 0xFFFFFFFF):
            raise ValueError("component id must be a 32-bit unsigned integer")
        self.id = id

    @property
    def type(self) -> int:
        return self.TYPE

    def _base_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"type": self.type}
        if self.id is not None:
            payload["id"] = self.id
        return payload

    @abstractmethod
    def to_payload(self) -> dict[str, Any]:
        """Serialize this component to a Discord Component Object."""

    @classmethod
    @abstractmethod
    def from_payload(cls, payload: dict[str, Any]) -> "Component":
        """Restore this component from a Discord Component Object."""
