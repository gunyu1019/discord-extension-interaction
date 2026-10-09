"""Register new Discord component payload models."""

from ..domain.container import Container
from ..domain.file_component import File
from ..domain.media_gallery import MediaGallery
from ..domain.section import Section
from ..domain.separator import Separator
from ..domain.text_display import TextDisplay
from ..domain.thumbnail import Thumbnail
from ..domain.user_select import UserSelect
from ..domain.role_select import RoleSelect
from .components import ComponentRegistry


_registry = ComponentRegistry()
for _model in (Section, TextDisplay, Thumbnail, MediaGallery, File, Separator, Container,
               UserSelect, RoleSelect):
    _registry.register(_model)


def parse_component_model(payload: dict):
    """Parse a new component, preserving future type numbers as unknown."""
    return _registry.from_payload(payload)
