"""MIT License

Copyright (c) 2021 gunyu1019

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import asyncio
import inspect
import discord
from enum import Enum
from typing import List, Optional, Union, Callable

from .utils import get_as_snowflake, get_enum


class ApplicationCommandType(Enum):
    CHAT_INPUT = 1
    USER = 2
    MESSAGE = 3


# OptionType
class Mentionable:
    pass


# Option
class CommandOptionChoice:
    def __init__(
            self,
            name: str,
            value: Union[int, str, float],
    ):
        self.name = name
        self.value = value

    @classmethod
    def from_payload(cls, data):
        return cls(
            name=data['name'],
            value=data['value']
        )

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'value': self.value
        }


class CommandOption:
    def __init__(
            self,
            name: str = None,
            option_type: type = None,
            description: str = "No description.",
            choices: List[CommandOptionChoice] = None,
            required: bool = False
    ):
        if choices is None:
            choices = []
        self.name = name
        self.type = option_type
        self.description = description
        self.choices = choices
        self.required = required

    @property
    def _get_type_id(self) -> int:
        if str in self.type.__mro__:
            return 3
        elif int in self.type.__mro__:
            return 4
        elif bool in self.type.__mro__:
            return 5
        elif discord.User in self.type.__mro__:
            return 6
        elif discord.abc.GuildChannel in self.type.__mro__:
            return 7
        elif discord.Role in self.type.__mro__:
            return 8
        elif Mentionable in self.type.__mro__:
            return 9
        elif float in self.type.__mro__:
            return 10
        raise TypeError("option type invalid (Subcommand and Subcommand Group, please use decorator)")

    def to_dict(self) -> dict:
        data = {
            "name": self.name,
            "description": self.description,
            "type": self._get_type_id,
            "required": self.required,
            "choices": [
                choice.to_dict() for choice in self.choices
            ]
        }
        return data


class ApplicationCommand:
    def __init__(
            self,
            name: str,
            description: str,
            default_permission: bool,
            guild_id: Optional[int] = None,
            command_type: ApplicationCommandType = ApplicationCommandType.CHAT_INPUT
    ):
        self.id: int = 0  # default: None
        self.name: str = name
        self.type: ApplicationCommandType = command_type
        self.application_id: int = 0  # default: None
        self.guild_id: Optional[int] = guild_id
        self.description: str = description
        self.default_permission: Optional[bool] = default_permission
        self.version: int = 1  # default: None

    @classmethod
    def from_payload(cls, data: dict):
        new_cls = cls(
            name=data['name'],
            description=data['description'],
            default_permission=data['default_permission'],
            guild_id=data.get('guild_id')
        )

        for key in (
                'id',
                'application_id',
                'version'
        ):
            value = data.get(key)
            setattr(new_cls, key, value)
        command_type = data['type']
        new_cls.type = get_enum(ApplicationCommandType, command_type)
        return new_cls

    def to_register_dict(self) -> dict:
        data = {
            "name": self.name,
            "type": self.type.value,
            "description": self.description
        }
        if self.default_permission is not None:
            data['default_permission'] = self.default_permission
        return data

    def __eq__(self, other):
        default_permission = self.default_permission or True
        return (
            self.name == other.name and
            self.description == other.description and
            default_permission == other.default_permission
        )

    def __ne__(self, other):
        return not self.__eq__(other)


class SlashCommand(ApplicationCommand):
    def __init__(
            self,
            options: List[CommandOption] = None,
            **kwargs
    ):
        if options is None:
            options = []
        super().__init__(**kwargs)
        self.type = ApplicationCommandType.CHAT_INPUT
        self.options: List[CommandOption] = options

    @classmethod
    def from_payload(cls, data: dict):
        new_cls = super().from_payload(data)
        new_cls.options = []
        return new_cls

    def to_register_dict(self) -> dict:
        data = super().to_register_dict()
        data['options'] = [opt.to_dict() for opt in self.options]
        return data


class UserCommand(ApplicationCommand):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = ApplicationCommandType.USER


class ContextMenu(ApplicationCommand):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = ApplicationCommandType.MESSAGE


# For Decorator
command_types = Union[SlashCommand, UserCommand, ContextMenu]


class BaseCommand:
    def __init__(self, func: Callable, checks=None, sync_command: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.func = func

        if checks is None:
            checks = []
        if hasattr(func, '__commands_checks__'):
            decorator_checks = getattr(func, '__commands_checks__')
            decorator_checks.reverse()
            checks += decorator_checks
        self.checks: list = checks

        self.sync_command: bool = sync_command
        self.cog = None

    @property
    def callback(self) -> Callable:
        return self.func

    def add_check(self, func) -> None:
        self.checks.append(func)

    def remove_check(self, func) -> None:
        try:
            self.checks.remove(func)
        except ValueError:
            pass


class Command(BaseCommand, SlashCommand):
    def __init__(self, func: Callable, checks=None, sync_command: bool = False, **kwargs):

        options: List[CommandOption] = kwargs.pop('options')
        signature_arguments = inspect.signature(func).parameters
        arguments = []
        if len(options) == 0 and len(signature_arguments) > 1:
            for _ in range(
                    len(signature_arguments) - 1
            ):
                options.append(
                    CommandOption()
                )
        elif len(signature_arguments) != len(options) + 1:
            raise TypeError("number of options and the number of arguments are different.")

        sign_arguments = list(signature_arguments.values())
        for arg in sign_arguments[1:]:
            arguments.append(arg)

        for index, opt in enumerate(options):
            if opt.name is None:
                options[index].name = arguments[index + 1].name
            if opt.type is None:
                options[index].type = arguments[index + 1].annotation
            if opt.required and arguments[index + 1].default != arguments[index + 1].empty:
                options[index].required = True
        super().__init__(func=func, checks=checks, sync_command=sync_command, options=options, **kwargs)


class MemberCommand(BaseCommand, UserCommand):
    pass


class ContextMenuCommand(BaseCommand, ContextMenu):
    pass


def command(
        name: str = None,
        description: str = "No description.",
        cls: classmethod = None,
        checks=None,
        options: List[CommandOption] = None,
        sync_command: bool = False,
        default_permission: bool = None
):
    if options is None:
        options = []

    if cls is None:
        cls = Command

    def decorator(func):
        return cls(
            func,
            name=name,
            description=description,
            checks=checks,
            options=options,
            sync_command=sync_command,
            default_permission=default_permission
        )

    return decorator


def user(
        name: str = None,
        cls: classmethod = None,
        checks=None,
        sync_command: bool = False,
        default_permission: bool = None
):
    if cls is None:
        cls = MemberCommand

    def decorator(func):
        return cls(
            func,
            name=name,
            checks=checks,
            sync_command=sync_command,
            default_permission=default_permission
        )

    return decorator


def context(
        name: str = None,
        cls: classmethod = None,
        checks=None,
        sync_command: bool = False,
        default_permission: bool = None
):
    if cls is None:
        cls = ContextMenuCommand

    def decorator(func):
        return cls(
            func,
            name=name,
            checks=checks,
            sync_command=sync_command,
            default_permission=default_permission
        )

    return decorator
