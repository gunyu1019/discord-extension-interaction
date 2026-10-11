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

__title__ = "Discord-Extension-Interaction"
__author__ = "gunyu1019"
__license__ = "MIT"
__copyright__ = "Copyright 2021-present gunyu1019"
__version__ = "0.8.0"  # discord.py v2.6+ support

from typing import NamedTuple, Literal, Optional

from discord.ext.interaction.implementation.client import Client, AutoShardedClient
from discord.ext.interaction.implementation.checks import *
from discord.ext.interaction.models.enums import (
    ApplicationCommandType,
    ApplicationContextType,
    ApplicationIntegrationType,
    Locale,
)
from discord.ext.interaction.models.commands import (
    CommandOption,
    CommandOptionChoice,
    ContextMenu,
    UserCommand,
    SlashCommand,
    ApplicationSubcommandGroup,
    ApplicationSubcommand,
    ApplicationCommand,
    Mentionable,
    option,
)
from discord.ext.interaction.implementation.core import (
    Command,
    ContextMenuCommand,
    SubCommandGroup,
    SubCommand,
    MemberCommand,
    command,
    user,
    context,
)
from discord.ext.interaction.implementation.components import (
    Components,
    ActionRow,
    Label,
    Button,
    Selection,
    TextInput,
    SelectOption,
    DetectComponent,
    detect_component,
)
from discord.ext.interaction.models.text_display import TextDisplay
from discord.ext.interaction.models.separator import Separator
from discord.ext.interaction.models.section import Section
from discord.ext.interaction.models.container import Container
from discord.ext.interaction.models.thumbnail import Thumbnail
from discord.ext.interaction.models.unfurled_media_item import UnfurledMediaItem
from discord.ext.interaction.models.media_gallery import MediaGallery, MediaGalleryItem
from discord.ext.interaction.models.file_component import File
from discord.ext.interaction.models.user_select import UserSelect
from discord.ext.interaction.models.role_select import RoleSelect
from discord.ext.interaction.models.mentionable_select import MentionableSelect
from discord.ext.interaction.models.channel_select import ChannelSelect
from discord.ext.interaction.models.select_default_value import SelectDefaultValue
from discord.ext.interaction.models.file_upload import FileUpload
from discord.ext.interaction.models.radio_group import RadioGroup, RadioGroupOption
from discord.ext.interaction.models.checkbox_group import (
    CheckboxGroup,
    CheckboxGroupOption,
)
from discord.ext.interaction.models.checkbox import Checkbox
from discord.ext.interaction.models.activity_command import (
    ActivityCommand,
    ActivityHandler,
)
from discord.ext.interaction.models.command_permissions import (
    CommandPermission,
    CommandPermissionType,
    GuildCommandPermissions,
)
from discord.ext.interaction.models.command_scope import GlobalScope, GuildScope
from discord.ext.interaction.models.sync_command import SyncCommand
from discord.ext.interaction.implementation.command_permissions_api import (
    CommandPermissionsAPI,
)
from discord.ext.interaction.models.errors import InvalidArgument, AlreadyDeferred
from discord.ext.interaction.implementation.interaction import (
    InteractionContext,
    ApplicationContext,
    SubcommandContext,
    ComponentsContext,
    AutocompleteContext,
    ModalSubmitContext,
)
from discord.ext.interaction.implementation.message import (
    Message,
    MessageTransferable,
    MessageEditable,
)
from discord.ext.interaction.implementation.listener import listener


class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
    release_level: Optional[Literal["alpha", "beta", "candidate", "final"]]
    serial: int

    def to_string(self) -> str:
        _version_info = f"{self.major}.{self.minor}.{self.micro}"
        if self.release_level is not None:
            _version_info += "-{}".format(self.release_level) + str(self.serial)
        return _version_info


version_info: VersionInfo = VersionInfo(
    major=0, minor=8, micro=0, release_level=None, serial=0
)
