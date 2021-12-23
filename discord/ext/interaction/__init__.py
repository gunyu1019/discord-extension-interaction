

__title__ = 'discord'
__author__ = 'gunyu1019'
__license__ = 'MIT'
__copyright__ = 'Copyright 2021-present gunyu1019'
__version__ = '0.3.3-beta1'

from typing import NamedTuple, Literal

from .client import Client, AutoShardedClient
from .checks import *
from .commands import (
    CommandOption, Command, CommandOptionChoice, ContextMenuCommand, ContextMenu, UserCommand, SlashCommand,
    SubCommandGroup, SubCommand, ApplicationSubcommandGroup, ApplicationSubcommand,
    MemberCommand, ApplicationCommand, ApplicationCommandType, Mentionable, command, user, context, option
)
from .components import Components, ActionRow, Button, Selection, Options, DetectComponent, detect_component
from .errors import InvalidArgument, AlreadyDeferred
from .interaction import InteractionContext, ApplicationContext, ComponentsContext
from .message import Message, MessageSendable
from .listener import Listener, listener


class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
    release_level: Literal["alpha", "beta", "candidate", "final"]
    serial: int


version_info: VersionInfo = VersionInfo(major=0, minor=3, micro=3, release_level='beta', serial=1)
