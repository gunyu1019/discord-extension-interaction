"""Remember whether old per-command sync was explicitly requested."""

from dataclasses import dataclass


@dataclass(frozen=True)
class LegacySyncRequest:
    command: object
    explicit: bool
