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

__title__ = 'Discord-Extension-Interaction'
__author__ = 'gunyu1019'
__license__ = 'MIT'
__copyright__ = 'Copyright 2021-present gunyu1019'
__version__ = '0.5.5-beta'

from typing import NamedTuple, Literal

from .client import Client, AutoShardedClient
from .checks import *
from .commands import (
    CommandOption, Command, CommandOptionChoice, ContextMenuCommand, ContextMenu, UserCommand, SlashCommand,
    SubCommandGroup, SubCommand, ApplicationSubcommandGroup, ApplicationSubcommand,
    MemberCommand, ApplicationCommand, ApplicationCommandType, Mentionable, command, user, context, option
)
from .components import Components, ActionRow, Button, Selection, TextInput, Options, DetectComponent, detect_component
from .errors import InvalidArgument, AlreadyDeferred
from .interaction import (
    InteractionContext, ApplicationContext, SubcommandContext, ComponentsContext, AutocompleteContext, ModalContext
)
from .message import Message, MessageSendable, MessageEditable
from .listener import listener


class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
    release_level: Literal["alpha", "beta", "candidate", "final"]
    serial: int


version_info: VersionInfo = VersionInfo(major=0, minor=5, micro=2, release_level='beta', serial=0)
