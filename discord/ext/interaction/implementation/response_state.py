"""Track the one-time initial response for a Discord interaction."""

from enum import Enum

from discord.ext.interaction.models.errors import AlreadyDeferred


class ResponsePhase(Enum):
    NEW = "new"
    DEFERRED = "deferred"
    RESPONDED = "responded"


class ResponseState:
    """Advance only after Discord accepts an initial callback or edit."""

    def __init__(self):
        self.phase = ResponsePhase.NEW

    def ensure_initial_available(self) -> None:
        if self.phase is ResponsePhase.DEFERRED:
            raise AlreadyDeferred
        if self.phase is ResponsePhase.RESPONDED:
            raise RuntimeError("interaction already responded")

    def deferred(self) -> None:
        self.ensure_initial_available()
        self.phase = ResponsePhase.DEFERRED

    def responded(self) -> None:
        if self.phase is ResponsePhase.RESPONDED:
            raise RuntimeError("interaction already responded")
        self.phase = ResponsePhase.RESPONDED
