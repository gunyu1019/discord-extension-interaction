"""Discord Media Gallery and its item structure."""

from typing import Any

from .component import Component
from .unfurled_media_item import UnfurledMediaItem


class MediaGalleryItem:
    """One visual item with optional alt text and spoiler state."""

    def __init__(
        self,
        media: UnfurledMediaItem,
        *,
        description: str | None = None,
        spoiler: bool = False,
    ):
        if not isinstance(media, UnfurledMediaItem):
            raise TypeError("Media Gallery item media must be an UnfurledMediaItem")
        if description is not None and (
            not isinstance(description, str) or len(description) > 1024
        ):
            raise ValueError("Media Gallery item description exceeds 1024 characters")
        if type(spoiler) is not bool:
            raise ValueError("Media Gallery item spoiler must be a boolean")
        self.media = media
        self.description = description
        self.spoiler = spoiler

    def to_payload(self) -> dict[str, Any]:
        payload = {"media": self.media.to_payload(), "spoiler": self.spoiler}
        if self.description is not None:
            payload["description"] = self.description
        return payload

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "MediaGalleryItem":
        return cls(
            UnfurledMediaItem.from_payload(payload["media"]),
            description=payload.get("description"),
            spoiler=payload.get("spoiler", False),
        )


class MediaGallery(Component):
    """One to ten media items in a Components V2 message."""

    TYPE = 12

    def __init__(self, items: list[MediaGalleryItem], *, id: int | None = None):
        super().__init__(id=id)
        if not 1 <= len(items) <= 10 or not all(
            isinstance(item, MediaGalleryItem) for item in items
        ):
            raise ValueError("Media Gallery requires 1 to 10 items")
        self.items = list(items)

    def to_payload(self) -> dict[str, Any]:
        return {
            **self._base_payload(),
            "items": [item.to_payload() for item in self.items],
        }

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "MediaGallery":
        return cls(
            [MediaGalleryItem.from_payload(item) for item in payload["items"]],
            id=payload.get("id"),
        )
