"""Discord application command permission overwrite models."""

from dataclasses import dataclass
from enum import IntEnum


class CommandPermissionType(IntEnum):
    ROLE = 1
    USER = 2
    CHANNEL = 3


@dataclass(frozen=True)
class CommandPermission:
    id: int
    type: CommandPermissionType
    permission: bool

    def __post_init__(self):
        if type(self.id) is not int or self.id <= 0:
            raise ValueError("permission id must be a positive snowflake")
        object.__setattr__(self, "type", CommandPermissionType(self.type))
        if type(self.permission) is not bool:
            raise ValueError("permission must be a boolean")

    def to_payload(self) -> dict:
        return {"id": str(self.id), "type": int(self.type), "permission": self.permission}

    @classmethod
    def from_payload(cls, payload: dict) -> "CommandPermission":
        return cls(
            id=int(payload["id"]), type=CommandPermissionType(payload["type"]),
            permission=payload["permission"],
        )


@dataclass(frozen=True)
class GuildCommandPermissions:
    id: int
    application_id: int
    guild_id: int
    permissions: tuple[CommandPermission, ...]

    @classmethod
    def from_payload(cls, payload: dict) -> "GuildCommandPermissions":
        return cls(
            id=int(payload["id"]), application_id=int(payload["application_id"]),
            guild_id=int(payload["guild_id"]),
            permissions=tuple(CommandPermission.from_payload(item)
                              for item in payload.get("permissions", [])),
        )
