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

import logging

import discord

from .enums import ApplicationCommandType
from .errors import InvalidArgument
from .utils import get_enum

log = logging.getLogger(__name__)


# OptionType
class Mentionable:
    pass


# Option
class CommandOptionChoice:
    """Represents an application command option choice.

    Attributes
    ----------
    name: str
        The name of the choice. This is visible to the user; max 100 characters.
    value: str
        The name of the choice. This is not visible to the user; max 100 characters.
    """

    def __init__(
        self,
        name: str,
        value: int | str | float,
    ):
        self.name = name
        self.value = value

    @classmethod
    def from_payload(cls, data):
        return cls(name=data["name"], value=data["value"])

    def to_dict(self) -> dict:
        return {"name": self.name, "value": self.value}

    def __eq__(self, other):
        return self.name == other.name and self.value == other.value

    def __ne__(self, other):
        return not self.__eq__(other)


class CommandOption:
    """Represents an application command option.

    Attributes
    ----------
    description: str
        The description of the option; max 100 characters.
    choices: list[CommandOptionChoice]
        A list of choices for the command to choose from for this option.
    min_value: Union[float, int]
        For option type ``string``, the minimum allowed length; min 0, max 6000
    max_value: Optional[int]
        For option type ``string``, the maximum allowed length; min 1, max 6000
    required: bool
        Whether the option is required. (defaults to ``false``)
    autocomplete: bool
        Whether the option has autocomplete. (defaults to ``false``)
    """

    def __init__(
        self,
        name: str = None,
        option_type: type = None,
        description: str = "No description.",
        choices: list[CommandOptionChoice] = None,
        channel_type: discord.ChannelType | int = None,
        channel_types: list[discord.ChannelType | int] = None,
        min_value: float | int = None,
        max_value: float | int = None,
        required: bool = False,
        autocomplete: bool = False,
    ):
        if choices is None:
            choices = []
        self._name = name
        self._type = option_type
        self.description = description
        self.choices = choices
        self.required = required
        self.autocomplete = autocomplete

        self.parameter_name: str | None = None

        if option_type is not None:
            if (len(choices) > 0 or autocomplete) and not (
                int in option_type.__mro__
                or float in option_type.__mro__
                or str in option_type.__mro__
            ):
                raise TypeError(
                    "choices or autocomplete should only be used in integer, string, and float."
                )

        if len(self.choices) > 0 and self.autocomplete:
            log.warning("autocomplete may not be set to true if choices are present.")

        self._channel_type: list[int] | None = None
        if channel_type is not None or channel_types is not None:
            if option_type is not None:
                if discord.abc.GuildChannel not in option_type.__mro__:
                    raise TypeError(
                        "Channel options can be set only when they are set to a channel type."
                    )

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
                    if hasattr(x, "value"):
                        self._channel_type.append(x.value)
                    else:
                        self._channel_type.append(x)

        if option_type is not None:
            if min_value is not None and (
                int not in option_type.__mro__ and float not in option_type.__mro__
            ):
                raise TypeError(
                    "min_value can only be called when the parameter types are int and float."
                )
            if max_value is not None and (
                int not in option_type.__mro__ and float not in option_type.__mro__
            ):
                raise TypeError(
                    "max_value can only be called when the parameter types are int and float."
                )
        self.min_value: int | None = min_value
        self.max_value: int | None = max_value

    @classmethod
    def empty_option(cls):
        return cls(None, None)

    @property
    def name(self) -> str:
        """The name of the option"""
        if self._name is None:
            raise ValueError("The name of the option must be defined.")
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def type(self) -> type:
        """The type of the option"""
        if self._type is None:
            raise ValueError("The type of the option must be defined.")
        return self._type

    @property
    def channel_type(self) -> list[discord.ChannelType] | None:
        """A list of channel types that are allowed for this option."""
        if discord.abc.GuildChannel not in self.type.__mro__:
            return
        channel_type = []
        for x in self._channel_type:
            channel_type.append(get_enum(discord.ChannelType, x))
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
        raise TypeError(
            "option type invalid (Subcommand and Subcommand Group, please use decorator)"
        )

    def to_dict(self) -> dict:
        data = {
            "name": self.name,
            "description": self.description,
            "type": self._get_type_id,
            "required": self.required,
            "choices": [choice.to_dict() for choice in self.choices],
            "autocomplete": self.autocomplete,
        }
        if self._channel_type is not None:
            data["channel_types"] = self._channel_type
        if self.min_value is not None:
            data["min_value"] = self.min_value
        if self.max_value is not None:
            data["max_value"] = self.max_value
        return data

    def __eq__(self, other):
        default_check = (
            self.name == other.name
            and other._type in self._type.__mro__
            and self.description == other.description
            and self.choices == other.choices
            and self.required == other.required
            and self.autocomplete == other.autocomplete
        )
        if int in self._type.__mro__ or float in self._type.__mro__:
            default_check = (
                default_check
                and self.min_value == other.min_value
                and self.max_value == other.max_value
            )
        elif discord.abc.GuildChannel in self._type.__mro__:
            default_check = default_check and self._channel_type == other._channel_type
        return default_check

    def __ne__(self, other):
        return not self.__eq__(other)

    @classmethod
    def from_payload(cls, data: dict):
        new_cls = cls.empty_option()
        tp_v = data["type"]
        if tp_v == 1:
            return ApplicationSubcommand.from_payload(data)
        if tp_v == 2:
            return ApplicationSubcommandGroup.from_payload(data)

        for x in ("name", "description", "required", "autocomplete"):
            setattr(new_cls, x, data.get(x))
        # optional--default false
        if new_cls.required is None:
            new_cls.required = False
        if new_cls.autocomplete is None:
            new_cls.autocomplete = False

        new_cls._type = (
            str,
            int,
            bool,
            discord.User,
            discord.abc.GuildChannel,
            discord.Role,
            Mentionable,
            float,
            discord.Attachment,
        )[(tp_v - 3)]
        if new_cls.type == discord.abc.GuildChannel and "channel_types" in data.keys():
            new_cls._channel_type = data.get("channel_types", [])
        if (
            new_cls.type == int or new_cls.type == float
        ) and "min_value" in data.keys():
            new_cls.min_value = data.get("min_value")
        if (
            new_cls.type == int or new_cls.type == float
        ) and "max_value" in data.keys():
            new_cls.max_value = data.get("max_value")

        new_cls.choices = []
        choices = data.get("choices", [])
        if len(choices) > 0:
            for ch in choices:
                new_cls.choices.append(CommandOptionChoice.from_payload(ch))
        return new_cls


class ApplicationSubcommand:
    def __init__(
        self,
        name: str,
        description: str = "No description.",
        options: list[CommandOption] | None = None,
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
        new_cls = cls(name=data["name"], description=data["description"])
        if "options" in data:
            new_cls.options = [CommandOption.from_payload(x) for x in data["options"]]
        return new_cls

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "type": self._get_type_id,
            "options": [opt.to_dict() for opt in self.options],
        }

    def __eq__(self, other):
        default_check = (
            self.name == other.name
            and self.description == other.description
            and self.options == other.options
        )
        return default_check

    def __ne__(self, other):
        return not self.__eq__(other)


class ApplicationSubcommandGroup:
    def __init__(
        self,
        name: str,
        options: list[ApplicationSubcommand],
        description: str = "No description.",
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
            name=data["name"],
            description=data["description"],
            options=[ApplicationSubcommand.from_payload(x) for x in data["options"]],
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "type": self._get_type_id,
            "options": [opt.to_dict() for opt in self.options],
        }

    def __eq__(self, other):
        default_check = (
            self.name == other.name
            and self.description == other.description
            and self.options == other.options
        )
        return default_check

    def __ne__(self, other):
        return not self.__eq__(other)


class ApplicationCommand:
    """Represents an application command.

    Attributes
    ----------
    id: int
        The id of application command
    name: str
        The name of application command
    description: str
        The description of application command
    version: int
        The version of application command
    type: ApplicationCommandType
        The type of application command
    application_id: ApplicationCommandType
        The application id of application command
    guild_id: Optional[int]
        The guild id of application command for private command
    default_member_permissions: Optional[str]
        The default member permissions that can run this command
    """

    def __init__(
        self,
        name: str,
        description: str = None,
        guild_id: int | None = None,
        command_type: ApplicationCommandType = ApplicationCommandType.CHAT_INPUT,
        default_member_permissions: str = None,
    ):
        self.id: int = 0  # default: None
        self.name: str = name
        self.type: ApplicationCommandType = command_type
        self.application_id: int = 0  # default: None
        self.guild_id: int | None = guild_id
        self.description: str | None = description
        self.default_member_permissions: str | None = default_member_permissions
        self.version: int = 1  # default: None

    @classmethod
    def from_payload(cls, data: dict):
        new_cls = cls(
            name=data["name"],
            description=data["description"],
            default_member_permissions=data.get("default_member_permissions"),
            guild_id=data.get("guild_id"),
        )

        for key in ("id", "application_id", "version"):
            value = data.get(key)
            setattr(new_cls, key, value)
        command_type = data["type"]
        new_cls.type = get_enum(ApplicationCommandType, command_type)
        return new_cls

    def to_register_dict(self) -> dict:
        data = {
            "name": self.name,
            "type": self.type.value,
            "description": self.description,
        }
        if self.default_member_permissions is not None:
            data["default_member_permissions"] = self.default_member_permissions
        return data

    @property
    def is_guild(self) -> bool:
        """Whether a private command(guild command)"""
        return self.guild_id is not None

    def __eq__(self, other):
        description = self.description or ""
        return (
            self.name == other.name
            and self.type == other.type
            and description == other.description
            and self.default_member_permissions == other.default_member_permissions
        )

    def __ne__(self, other):
        return not self.__eq__(other)


class SlashCommand(ApplicationCommand):
    """Represents an application command for ``CHAT_INPUT`` type.

    Attributes
    ----------
    options: list[Union[CommandOption, ApplicationSubcommand, ApplicationSubcommandGroup]]
        A list of options for application command.
    """

    def __init__(
        self,
        options: list[
            CommandOption | ApplicationSubcommandGroup | ApplicationSubcommand
        ] = None,
        **kwargs
    ):
        if options is None:
            options = []
        super().__init__(**kwargs)
        self.type = ApplicationCommandType.CHAT_INPUT
        self.options: list[
            CommandOption | ApplicationSubcommand | ApplicationSubcommandGroup
        ] = options

    def __eq__(self, other):
        return super().__eq__(other) and self.options == other.options

    def __ne__(self, other):
        return not self.__eq__(other)

    @classmethod
    def from_payload(cls, data: dict):
        new_cls = super().from_payload(data)
        new_cls.options = [
            CommandOption.from_payload(opt) for opt in data.get("options", [])
        ]
        return new_cls

    def to_register_dict(self) -> dict:
        data = super().to_register_dict()
        data["options"] = [opt.to_dict() for opt in self.options]
        return data


class UserCommand(ApplicationCommand):
    """Represents an application command for ``User`` type."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = ApplicationCommandType.USER


class ContextMenu(ApplicationCommand):
    """Represents an application command for ``Context Menu`` type."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = ApplicationCommandType.MESSAGE


command_types = SlashCommand | UserCommand | ContextMenu


def from_payload(data: dict) -> command_types:
    if data["type"] == ApplicationCommandType.CHAT_INPUT:
        _result = SlashCommand.from_payload(data)
    elif data["type"] == ApplicationCommandType.USER:
        _result = UserCommand.from_payload(data)
    elif data["type"] == ApplicationCommandType.MESSAGE:
        _result = ContextMenu.from_payload(data)
    else:
        _result = ApplicationCommand.from_payload(data)
    return _result


# For Decorator
def option(
    name: str = None,
    option_type: type = None,
    description: str = "No description.",
    choices: list[CommandOptionChoice] = None,
    channel_type: discord.ChannelType | int = None,
    channel_types: list[discord.ChannelType | int] = None,
    min_value: float | int = None,
    max_value: float | int = None,
    required: bool = False,
    autocomplete: bool = False,
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
        autocomplete=autocomplete,
    )

    def decorator(func):
        if hasattr(func, "options") or isinstance(func, SlashCommand):
            func.options.append(options)
        else:
            if not hasattr(func, "__command_options__"):
                func.__command_options__ = []
            func.__command_options__.append(options)
        return func

    return decorator
