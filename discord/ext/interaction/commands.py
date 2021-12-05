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

import inspect
from enum import Enum
from typing import List, Optional, Union, Callable

import discord

from .utils import get_enum


class ApplicationCommandType(Enum):
    CHAT_INPUT = 1
    USER = 2
    MESSAGE = 3

    def __eq__(self, other):
        if isinstance(other, ApplicationCommandType):
            return self._value_ == other.value
        return self._value_ == other

    def __ne__(self, other):
        return not self.__eq__(other)


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

    def __eq__(self, other):
        return (
                self.name == other.name and
                self.value == other.value
        )

    def __ne__(self, other):
        return not self.__eq__(other)


class CommandOption:
    def __init__(
            self,
            name: str = None,
            option_type: type = None,
            description: str = "No description.",
            choices: List[CommandOptionChoice] = None,
            channel_type: Union[discord.ChannelType, int] = None,
            channel_types: List[Union[discord.ChannelType, int]] = None,
            min_value: Union[float, int] = None,
            max_value: Union[float, int] = None,
            required: bool = False
    ):
        if choices is None:
            choices = []
        self.name = name
        self.type = option_type
        self.description = description
        self.choices = choices
        self.required = required

        self._channel_type: Optional[List[int]] = None
        if channel_type is not None or channel_types is not None:
            if option_type is not None:
                if discord.abc.GuildChannel not in option_type.__mro__:
                    raise TypeError

            if channel_types is not None and channel_type is not None:
                raise TypeError
            elif channel_type is not None:
                if isinstance(channel_type, discord.ChannelType):
                    self._channel_type = [channel_type.value]
                else:
                    self._channel_type = [channel_type]
            elif channel_types is not None:
                self._channel_type = []
                for x in channel_types:
                    if isinstance(x, discord.ChannelType):
                        self._channel_type.append(x.value)
                    else:
                        self._channel_type.append(x)

        if option_type is not None:
            if min_value is not None and (int not in option_type.__mro__ and float not in option_type.__mro__):
                raise TypeError
            if max_value is not None and (int not in option_type.__mro__ and float not in option_type.__mro__):
                raise TypeError
        self.min_value: Optional[int] = min_value
        self.max_value: Optional[int] = max_value

    @property
    def channel_type(self) -> Optional[List[discord.ChannelType]]:
        if discord.abc.GuildChannel not in self.type.__mro__:
            return
        channel_type = []
        for x in self._channel_type:
            channel_type.append(
                get_enum(discord.ChannelType, x)
            )
        return channel_type

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
        if self._channel_type is not None:
            data['channel_types'] = self._channel_type
        if self.min_value is not None:
            data['min_value'] = self._channel_type
        if self.max_value is not None:
            data['max_value'] = self._channel_type
        return data

    def __eq__(self, other):
        return (
                self.name == other.name and
                self.type == other.type and
                self.description == other.description and
                self.choices == other.choices and
                self.required == other.required
        )

    def __ne__(self, other):
        return not self.__eq__(other)


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

    @property
    def is_guild(self) -> bool:
        return self.guild_id is not None

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

    def __eq__(self, other):
        return (
                super().__eq__(other) and
                self.options == other.options
        )

    def __ne__(self, other):
        return not self.__eq__(other)

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


command_types = Union[SlashCommand, UserCommand, ContextMenu]
channel_types = (
    discord.TextChannel,
    discord.VoiceChannel,
    discord.DMChannel,
    discord.StageChannel,
    discord.GroupChannel,
    discord.CategoryChannel,
    discord.StoreChannel
)


def from_payload(data: dict) -> command_types:
    if data['type'] == ApplicationCommandType.CHAT_INPUT:
        _result = SlashCommand.from_payload(data)
    elif data['type'] == ApplicationCommandType.USER:
        _result = UserCommand.from_payload(data)
    elif data['type'] == ApplicationCommandType.MESSAGE:
        _result = ContextMenu.from_payload(data)
    else:
        _result = ApplicationCommand.from_payload(data)
    return _result


# For Decorator


class BaseCommand:
    def __init__(self, func: Callable, checks=None, sync_command: bool = False, *args, **kwargs):
        if kwargs.get('name') is None:
            kwargs['name'] = func.__name__
        super().__init__(*args, **kwargs)

        self.func = func

        if checks is None:
            checks = []
        if hasattr(func, '__commands_checks__'):
            decorator_checks = getattr(func, '__commands_checks__')
            decorator_checks.reverse()
            checks += decorator_checks
        self.checks: list = checks

        self.permissions: list = []
        if hasattr(func, '__commands_permissions__'):
            decorator_permissions = getattr(func, '__commands_permissions__')
            self.permissions += decorator_permissions

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
    def __init__(
            self,
            func: Callable,
            checks=None,
            options: List[CommandOption] = None,
            sync_command: bool = False,
            **kwargs
    ):
        if options is None:
            options = []
        if hasattr(func, '__command_options__'):
            options += func.__command_options__

        signature_arguments = inspect.signature(func).parameters
        arguments = []
        if len(options) == 0 and len(signature_arguments) > 0:
            for _ in range(
                    len(signature_arguments) - 1
            ):
                options.append(
                    CommandOption()
                )
        elif len(signature_arguments) - 1 > len(options):
            for _ in range(
                    len(signature_arguments) - len(options) - 1
            ):
                options.append(CommandOption())
        elif len(signature_arguments) - 1 < len(options):
            raise TypeError("number of options and the number of arguments are different.")

        sign_arguments = list(signature_arguments.values())
        for arg in sign_arguments[1:]:
            arguments.append(arg)

        for index, opt in enumerate(options):
            if opt.name is None:
                options[index].name = arguments[index].name
            if opt.type is None:
                options[index].type = arguments[index].annotation
            if opt.required or arguments[index].default == arguments[index].empty:
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


def option(
        name: str = None,
        option_type: type = None,
        description: str = "No description.",
        choices: List[CommandOptionChoice] = None,
        channel_type: Union[discord.ChannelType, int] = None,
        channel_types: List[Union[discord.ChannelType, int]] = None,
        min_value: Union[float, int] = None,
        max_value: Union[float, int] = None,
        required: bool = False
):
    options = CommandOption(
        name=name,
        option_type=option_type,
        description=description,
        choices=choices,
        channel_type=channel_type,
        channel_types=channel_types,
        min_value=min_value,
        max_value=max_value,
        required=required
    )

    def decorator(func):
        if hasattr(func, 'options') or isinstance(func, SlashCommand):
            func.options.append(options)
        else:
            if not hasattr(func, '__command_options__'):
                func.__command_options__ = []
            func.__command_options__.append(options)
        return func

    return decorator
