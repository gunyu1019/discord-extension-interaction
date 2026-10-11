"""Discord File component for displaying an uploaded attachment."""

from typing import Any

from discord.ext.interaction.models.component import Component
from discord.ext.interaction.models.unfurled_media_item import UnfurledMediaItem


class File(Component):
    """A file shown in a Components V2 message."""

    TYPE = 13

    def __init__(
        self,
        file: UnfurledMediaItem,
        *,
        spoiler: bool = False,
        name: str | None = None,
        size: int | None = None,
        id: int | None = None,
        _received: bool = False,
    ):
        super().__init__(id=id)
        if not isinstance(file, UnfurledMediaItem) or not (
            file.url.startswith("attachment://")
            or _received
            and file.url.startswith("https://")
        ):
            raise ValueError("File requires an attachment:// media reference")
        if type(spoiler) is not bool:
            raise ValueError("File spoiler must be a boolean")
        self.file = file
        self.spoiler = spoiler
        self.name = name
        self.size = size

    def to_payload(self) -> dict[str, Any]:
        payload = {
            **self._base_payload(),
            "file": self.file.to_payload(),
            "spoiler": self.spoiler,
        }
        if self.name is not None:
            payload["name"] = self.name
        if self.size is not None:
            payload["size"] = self.size
        return payload

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "File":
        return cls(
            UnfurledMediaItem.from_payload(payload["file"]),
            spoiler=payload.get("spoiler", False),
            name=payload.get("name"),
            size=payload.get("size"),
            id=payload.get("id"),
            _received=True,
        )
