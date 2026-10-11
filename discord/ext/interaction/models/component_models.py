"""Register new Discord component payload models."""

from discord.ext.interaction.models.container import Container
from discord.ext.interaction.models.file_component import File
from discord.ext.interaction.models.media_gallery import MediaGallery
from discord.ext.interaction.models.section import Section
from discord.ext.interaction.models.separator import Separator
from discord.ext.interaction.models.text_display import TextDisplay
from discord.ext.interaction.models.thumbnail import Thumbnail
from discord.ext.interaction.models.user_select import UserSelect
from discord.ext.interaction.models.role_select import RoleSelect
from discord.ext.interaction.models.mentionable_select import MentionableSelect
from discord.ext.interaction.models.channel_select import ChannelSelect
from discord.ext.interaction.models.file_upload import FileUpload
from discord.ext.interaction.models.radio_group import RadioGroup
from discord.ext.interaction.models.checkbox_group import CheckboxGroup
from discord.ext.interaction.models.checkbox import Checkbox
from discord.ext.interaction.models.component_codec import ComponentRegistry

_registry = ComponentRegistry()
for _model in (
    Section,
    TextDisplay,
    Thumbnail,
    MediaGallery,
    File,
    Separator,
    Container,
    UserSelect,
    RoleSelect,
    MentionableSelect,
    ChannelSelect,
    FileUpload,
    RadioGroup,
    CheckboxGroup,
    Checkbox,
):
    _registry.register(_model)


def parse_component_model(payload: dict):
    """Parse a new component, preserving future type numbers as unknown."""
    return _registry.from_payload(payload)
