from typing import List
from enum import Enum

from .commands import BaseCommand
from .utils import get_enum


class PermissionType(Enum):
    ROLE = 1
    USER = 2


class CommandPermission:
    def __init__(
            self,
            id: int,
            type: PermissionType,
            permission: bool
    ):
        self.id = id
        self.type = type
        self.permission = permission

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'type': self.type.value,
            'permission': self.permission
        }

    @classmethod
    def from_payload(cls, data: dict):
        permission_type = get_enum(PermissionType, data['type'])
        return cls(
            id=data['id'],
            type=permission_type,
            permission=data['permission']
        )


class ApplicationCommandPermission:
    def __init__(
            self,
            permissions: List[CommandPermission] = None
    ):
        self.id: int = -1
        self.guild_id: int = -1
        self.application_id: int = -1

        if permissions is None:
            permissions = []
        self.permissions = permissions

    def to_dict(self) -> dict:
        return {
            'permissions': [
                x.to_dict() for x in self.permissions
            ]
        }

    @classmethod
    def from_payload(cls, data: dict):
        new_cls = cls(
            permissions=[
                CommandPermission.from_payload(x) for x in data['permissions']
            ]
        )
        new_cls.id = data['id']
        new_cls.application_id = data['application_id']
        new_cls.guild_id = data['guild_id']
        return new_cls


def permissions(
        id: int,
        guild_id: int,
        type: PermissionType,
        permission: bool
):
    cls = CommandPermission(
        id=id,
        type=type,
        permission=permission
    )

    def decorator(func):
        if hasattr(func, 'permissions') or isinstance(func, BaseCommand):
            func.permissions.append(cls)
        else:
            if not hasattr(func, '__command_permissions__'):
                func.__command_permissions__ = []
            func.__command_permissions__.append((guild_id, cls))
        return func
    return decorator
