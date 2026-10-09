"""Register the currently supported Components V2 payload models."""

from ..domain.container import Container
from ..domain.file_component import File
from ..domain.media_gallery import MediaGallery
from ..domain.section import Section
from ..domain.separator import Separator
from ..domain.text_display import TextDisplay
from ..domain.thumbnail import Thumbnail
from .components import ComponentRegistry


_registry = ComponentRegistry()
for _model in (Section, TextDisplay, Thumbnail, MediaGallery, File, Separator, Container):
    _registry.register(_model)


def parse_v2_component(payload: dict):
    """Parse a V2 component, preserving future type numbers as unknown."""
    return _registry.from_payload(payload)
