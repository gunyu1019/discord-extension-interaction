"""Discord Thumbnail accessory component."""

from typing import Any

from .component import Component
from .unfurled_media_item import UnfurledMediaItem


class Thumbnail(Component):
    """An image accessory for a Section."""

    TYPE = 11

    def __init__(
        self,
        media: UnfurledMediaItem,
        *,
        description: str | None = None,
        spoiler: bool = False,
        id: int | None = None,
    ):
        super().__init__(id=id)
        if not isinstance(media, UnfurledMediaItem):
            raise TypeError("Thumbnail media must be an UnfurledMediaItem")
        if description is not None and (
            not isinstance(description, str) or len(description) > 1024
        ):
            raise ValueError("Thumbnail description exceeds 1024 characters")
        if type(spoiler) is not bool:
            raise ValueError("Thumbnail spoiler must be a boolean")
        self.media = media
        self.description = description
        self.spoiler = spoiler

    def to_payload(self) -> dict[str, Any]:
        payload = {
            **self._base_payload(),
            "media": self.media.to_payload(),
            "spoiler": self.spoiler,
        }
        if self.description is not None:
            payload["description"] = self.description
        return payload

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "Thumbnail":
        return cls(
            UnfurledMediaItem.from_payload(payload["media"]),
            description=payload.get("description"),
            spoiler=payload.get("spoiler", False),
            id=payload.get("id"),
        )
