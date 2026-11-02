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

from .client import Client, AutoShardedClient
from .checks import *
from .enums import (
    ApplicationCommandType,
    ApplicationContextType,
    ApplicationIntegrationType,
    Locale,
)
from .commands import (
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
from .core import (
    Command,
    ContextMenuCommand,
    SubCommandGroup,
    SubCommand,
    MemberCommand,
    command,
    user,
    context,
)
from .components import (
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
from .models.text_display import TextDisplay
from .models.separator import Separator
from .models.section import Section
from .models.container import Container
from .models.thumbnail import Thumbnail
from .models.unfurled_media_item import UnfurledMediaItem
from .models.media_gallery import MediaGallery, MediaGalleryItem
from .models.file_component import File
from .models.user_select import UserSelect
from .models.role_select import RoleSelect
from .models.mentionable_select import MentionableSelect
from .models.channel_select import ChannelSelect
from .models.select_default_value import SelectDefaultValue
from .models.file_upload import FileUpload
from .models.radio_group import RadioGroup, RadioGroupOption
from .models.checkbox_group import (
    CheckboxGroup,
    CheckboxGroupOption,
)
from .models.checkbox import Checkbox
from .models.activity_command import (
    ActivityCommand,
    ActivityHandler,
)
from .models.command_permissions import (
    CommandPermission,
    CommandPermissionType,
    GuildCommandPermissions,
)
from .models.command_scope import GlobalScope, GuildScope
from .models.sync_command import SyncCommand
from .command_permissions_api import (
    CommandPermissionsAPI,
)
from .errors import InvalidArgument, AlreadyDeferred
from .interaction import (
    InteractionContext,
    ApplicationContext,
    SubcommandContext,
    ComponentsContext,
    AutocompleteContext,
    ModalSubmitContext,
)
from .message import (
    Message,
    MessageTransferable,
    MessageEditable,
)
from .listener import listener


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
