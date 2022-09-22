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
import logging
from enum import Enum
from typing import List, Optional, Union, Callable, Coroutine, Any

import discord

from .errors import InvalidArgument
from .utils import get_enum, async_all

log = logging.getLogger(__name__)


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
            required: bool = False,
            autocomplete: bool = False
    ):
        if choices is None:
            choices = []
        self.name = name
        self.type = option_type
        self.description = description
        self.choices = choices
        self.required = required
        self.autocomplete = autocomplete

        self.parameter_name: Optional[str] = None

        if option_type is not None:
            if (
                    (len(choices) > 0 or autocomplete) and
                    not (int in option_type.__mro__ or float in option_type.__mro__ or str in option_type.__mro__)
            ):
                raise TypeError('choices or autocomplete should only be used in integer, string, and float.')

        if len(self.choices) > 0 and self.autocomplete:
            log.warning("autocomplete may not be set to true if choices are present.")

        self._channel_type: Optional[List[int]] = None
        if channel_type is not None or channel_types is not None:
            if option_type is not None:
                if discord.abc.GuildChannel not in option_type.__mro__:
                    raise TypeError('Channel options can be set only when they are set to a channel type.')

            if channel_types is not None and channel_type is not None:
                raise InvalidArgument()
            elif channel_type is not None:
                if isinstance(channel_type, discord.ChannelType):
                    self._channel_type = [getattr(channel_type, "value", 0)]
                else:
                    self._channel_type = [channel_type]
            elif channel_types is not None:
                self._channel_type = []
                for x in channel_types:
                    if hasattr(x, 'value'):
                        self._channel_type.append(x.value)
                    else:
                        self._channel_type.append(x)

        if option_type is not None:
            if min_value is not None and (int not in option_type.__mro__ and float not in option_type.__mro__):
                raise TypeError('min_value can only be called when the parameter types are int and float.')
            if max_value is not None and (int not in option_type.__mro__ and float not in option_type.__mro__):
                raise TypeError('max_value can only be called when the parameter types are int and float.')
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
        if ApplicationSubcommand in self.type.__mro__:
            return 1
        elif ApplicationSubcommandGroup in self.type.__mro__:
            return 2
        elif str == self.type:
            return 3
        elif int == self.type:
            return 4
        elif bool == self.type:
            return 5
        elif discord.User in self.type.__mro__:
            return 6
        elif discord.abc.GuildChannel in self.type.__mro__:
            return 7
        elif discord.Role in self.type.__mro__:
            return 8
        elif Mentionable in self.type.__mro__:
            return 9
        elif float == self.type:
            return 10
        elif discord.Attachment == self.type:
            return 11
        raise TypeError("option type invalid (Subcommand and Subcommand Group, please use decorator)")

    def to_dict(self) -> dict:
        data = {
            "name": self.name,
            "description": self.description,
            "type": self._get_type_id,
            "required": self.required,
            "choices": [
                choice.to_dict() for choice in self.choices
            ],
            "autocomplete": self.autocomplete
        }
        if self._channel_type is not None:
            data['channel_types'] = self._channel_type
        if self.min_value is not None:
            data['min_value'] = self.min_value
        if self.max_value is not None:
            data['max_value'] = self.max_value
        return data

    def __eq__(self, other):
        default_check = (
                self.name == other.name and
                other.type in self.type.__mro__ and
                self.description == other.description and
                self.choices == other.choices and
                self.required == other.required and
                self.autocomplete == other.autocomplete
        )
        if int in self.type.__mro__ or float in self.type.__mro__:
            default_check = default_check and self.min_value == other.min_value and self.max_value == other.max_value
        elif discord.abc.GuildChannel in self.type.__mro__:
            default_check = default_check and self._channel_type == other._channel_type
        return default_check

    def __ne__(self, other):
        return not self.__eq__(other)

    @classmethod
    def from_payload(cls, data: dict):
        new_cls = cls()
        tp_v = data['type']
        if tp_v == 1:
            return ApplicationSubcommand.from_payload(data)
        if tp_v == 2:
            return ApplicationSubcommandGroup.from_payload(data)

        for x in ('name', 'description', 'required', 'autocomplete'):
            setattr(
                new_cls, x, data.get(x)
            )
        # optional--default false
        if new_cls.required is None:
            new_cls.required = False
        if new_cls.autocomplete is None:
            new_cls.autocomplete = False

        new_cls.type = (
            str, int, bool, discord.User, discord.abc.GuildChannel, discord.Role, Mentionable, float
        )[(tp_v - 3)]
        if new_cls.type == discord.abc.GuildChannel and 'channel_types' in data.keys():
            new_cls._channel_type = data.get('channel_types', [])
        if (new_cls.type == int or new_cls.type == float) and 'min_value' in data.keys():
            new_cls.min_value = data.get('min_value')
        if (new_cls.type == int or new_cls.type == float) and 'max_value' in data.keys():
            new_cls.max_value = data.get('max_value')

        new_cls.choices = []
        choices = data.get('choices', [])
        if len(choices) > 0:
            for ch in choices:
                new_cls.choices.append(
                    CommandOptionChoice.from_payload(ch)
                )
        return new_cls


class ApplicationSubcommand:
    def __init__(
            self,
            name: str,
            description: str = "No description.",
            options: Optional[List[Union[CommandOption]]] = None
    ):
        self.name = name
        self.description = description
        if options is None:
            options = []
        self.options = options

    @property
    def _get_type_id(self) -> int:
        return 1

    @classmethod
    def from_payload(cls, data: dict):
        new_cls = cls(
            name=data['name'],
            description=data['description']
        )
        if 'options' in data:
            new_cls.options = [CommandOption.from_payload(x) for x in data['options']]
        return new_cls

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "type": self._get_type_id,
            "options": [opt.to_dict() for opt in self.options]
        }

    def __eq__(self, other):
        default_check = (
            self.name == other.name and
            self.description == other.description and
            self.options == other.options
        )
        return default_check

    def __ne__(self, other):
        return not self.__eq__(other)


class ApplicationSubcommandGroup:
    def __init__(
            self,
            name: str,
            options: List[ApplicationSubcommand],
            description: str = "No description."
    ):
        self.name = name
        self.description = description
        self.options = options

    @property
    def _get_type_id(self) -> int:
        return 2

    @classmethod
    def from_payload(cls, data: dict):
        return cls(
            name=data['name'],
            description=data['description'],
            options=[ApplicationSubcommand.from_payload(x) for x in data['options']]
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "type": self._get_type_id,
            "options": [opt.to_dict() for opt in self.options]
        }

    def __eq__(self, other):
        default_check = (
            self.name == other.name and
            self.description == other.description and
            self.options == other.options
        )
        return default_check

    def __ne__(self, other):
        return not self.__eq__(other)


class ApplicationCommand:
    def __init__(
            self,
            name: str,
            default_permission: bool,
            description: str = None,
            guild_id: Optional[int] = None,
            command_type: ApplicationCommandType = ApplicationCommandType.CHAT_INPUT
    ):
        self.id: int = 0  # default: None
        self.name: str = name
        self.type: ApplicationCommandType = command_type
        self.application_id: int = 0  # default: None
        self.guild_id: Optional[int] = guild_id
        self.description: Optional[str] = description
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
        description = self.description or ''
        return (
                self.name == other.name and
                self.type == other.type and
                description == other.description and
                default_permission == other.default_permission
        )

    def __ne__(self, other):
        return not self.__eq__(other)


class SlashCommand(ApplicationCommand):
    def __init__(
            self,
            options: List[Union[CommandOption, ApplicationSubcommandGroup, ApplicationSubcommand]] = None,
            **kwargs
    ):
        if options is None:
            options = []
        super().__init__(**kwargs)
        self.type = ApplicationCommandType.CHAT_INPUT
        self.options: List[Union[CommandOption, SubCommand, SubCommandGroup]] = options

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
        new_cls.options = [CommandOption.from_payload(opt) for opt in data.get('options', [])]
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
class BaseCore:
    def __init__(self, func: Callable, checks=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.func = func

        if checks is None:
            checks = []
        if hasattr(func, '__commands_checks__'):
            decorator_checks = getattr(func, '__commands_checks__')
            decorator_checks.reverse()
            checks += decorator_checks
        self.checks: list = checks
        self.cog = None

    def __call__(self, *args, **kwargs):
        return self.callback(*args, **kwargs)

    def callback(self, *args, **kwargs) -> Coroutine[Any, Any, Any]:
        if self.cog is None:
            return self.func(*args, **kwargs)
        return self.func(self.cog, *args, **kwargs)

    async def can_run(self, ctx):
        predicates = self.checks
        if len(predicates) == 0:
            # since we have no checks, then we just return True.
            return True

        return await async_all(predicate(ctx) for predicate in predicates)


# Subcommand
class SubCommand(BaseCore, ApplicationSubcommand):
    def __init__(self, func: Callable, parents, checks=None, *args, **kwargs):
        if kwargs.get('name') is None:
            kwargs['name'] = func.__name__
        self.parents: Union[Command, SubCommandGroup] = parents
        self.top_parents: Command = kwargs.pop('top_parents', self.parents)
        self.parents.options.append(self)

        options = kwargs.get('options')
        if options is None:
            options = []
        if hasattr(func, '__command_options__'):
            func.__command_options__.reverse()
            options += func.__command_options__
        self.base_options = options

        kwargs['options'] = get_signature_option(func, options)
        super().__init__(func=func, checks=checks, *args, **kwargs)


class SubCommandGroup(BaseCore, ApplicationSubcommandGroup):
    def __init__(self, func: Callable, parents, checks=None, *args, **kwargs):
        if kwargs.get('name') is None:
            kwargs['name'] = func.__name__
        self.parents: Union[Command] = parents
        super().__init__(func=func, checks=checks, *args, **kwargs)
        self.parents.options.append(self)

    def subcommand(
            self,
            name: str = None,
            description: str = "No description.",
            cls: classmethod = None,
            checks=None,
            options: Optional[List[CommandOption]] = None
    ):
        if options is None:
            options = []

        if cls is None:
            cls = SubCommand

        def decorator(func):
            return cls(
                func,
                name=name,
                description=description,
                checks=checks,
                options=options,
                top_parents=self.parents,
                parents=self
            )
        return decorator


class BaseCommand(BaseCore):
    def __init__(self, func: Callable, checks=None, sync_command: bool = None, *args, **kwargs):
        if kwargs.get('name') is None:
            kwargs['name'] = func.__name__
        super().__init__(func=func, checks=checks, *args, **kwargs)
        self.sync_command: bool = sync_command


class Command(BaseCommand, SlashCommand):
    def __init__(
            self,
            func: Callable,
            checks=None,
            options: List[Union[CommandOption, SubCommand, SubCommandGroup]] = None,
            sync_command: bool = None,
            **kwargs
    ):
        if options is None:
            options = []
        if hasattr(func, '__command_options__'):
            func.__command_options__.reverse()
            options += func.__command_options__
        self.base_options = options

        # options = get_signature_option(func, options)
        super().__init__(func=func, checks=checks, sync_command=sync_command, options=options, **kwargs)

    def subcommand(
            self,
            name: str = None,
            description: str = "No description.",
            cls: classmethod = None,
            checks=None,
            options: List[CommandOption] = None
    ):
        if options is None:
            options = []

        if cls is None:
            cls = SubCommand

        def decorator(func):
            new_cls = cls(
                func,
                name=name,
                description=description,
                checks=checks,
                options=options,
                top_parents=self,
                parents=self
            )

            return new_cls
        return decorator

    def subcommand_group(
            self,
            name: str = None,
            description: str = "No description.",
            cls: classmethod = None,
            options: list = None
    ):
        if options is None:
            options = []

        if cls is None:
            cls = SubCommandGroup

        def decorator(func):
            new_cls = cls(
                func,
                name=name,
                description=description,
                options=options,
                parents=self
            )
            return new_cls
        return decorator

    @property
    def is_subcommand(self) -> bool:
        for opt in self.options:
            if isinstance(opt, (SubCommand, SubCommandGroup)):
                return True
        else:
            return False


class MemberCommand(BaseCommand, UserCommand):
    pass


class ContextMenuCommand(BaseCommand, ContextMenu):
    pass


decorator_command_types = Union[Command, MemberCommand, ContextMenuCommand]


def command(
        name: str = None,
        description: str = "No description.",
        cls: classmethod = None,
        checks=None,
        options: List[CommandOption] = None,
        sync_command: bool = None,
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
        sync_command: bool = None,
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
        sync_command: bool = None,
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
        required: bool = False,
        autocomplete: bool = False
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
        required=required,
        autocomplete=autocomplete
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


def get_signature_option(
        func,
        options,
        skipping_argument: int = 1
):
    signature_arguments = inspect.signature(func).parameters
    arguments = []
    signature_arguments_count = len(signature_arguments) - skipping_argument

    if len(options) == 0 and len(signature_arguments) > skipping_argument - 1:
        for _ in range(signature_arguments_count):
            options.append(
                CommandOption()
            )
    elif signature_arguments_count > len(options):
        for _ in range(
                signature_arguments_count - len(options)
        ):
            options.append(CommandOption())
    elif signature_arguments_count < len(options):
        raise TypeError("number of options and the number of arguments are different.")

    sign_arguments = list(signature_arguments.values())
    for arg in sign_arguments[skipping_argument:]:
        arguments.append(arg)

    for index, opt in enumerate(options):
        options[index].parameter_name = arguments[index].name
        if opt.name is None:
            options[index].name = arguments[index].name
        if opt.required or arguments[index].default == arguments[index].empty:
            options[index].required = True
        if opt.type is None:
            options[index].type = arguments[index].annotation

        # Check Empty Option
        if arguments[index].annotation is None:
            del options[index]

    return options
