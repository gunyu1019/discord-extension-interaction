"""Discord File Upload modal input."""

from typing import Any

from discord.ext.interaction.models.component import Component


class FileUpload(Component):
    """Choose one or more files in a modal Label."""

    TYPE = 19

    def __init__(
        self,
        custom_id: str,
        *,
        min_values: int = 1,
        max_values: int = 1,
        required: bool = True,
        file_types: list[str] | None = None,
        values: list[str] | None = None,
        id: int | None = None,
    ):
        super().__init__(id=id)
        if not isinstance(custom_id, str) or not 1 <= len(custom_id) <= 100:
            raise ValueError("File Upload custom_id requires 1 to 100 characters")
        if (
            type(min_values) is not int
            or type(max_values) is not int
            or not 0 <= min_values <= max_values <= 10
        ):
            raise ValueError(
                "File Upload min_values/max_values must be between 0 and 10"
            )
        if type(required) is not bool or (required and min_values == 0):
            raise ValueError("required File Upload needs min_values >= 1")
        if file_types is not None and (
            len(file_types) > 10
            or any(
                not isinstance(item, str)
                or item not in ("image", "video", "audio")
                and not (item.startswith(".") and len(item) > 1)
                for item in file_types
            )
        ):
            raise ValueError(
                "File Upload file_types must be media categories or extensions"
            )
        self.custom_id = custom_id
        self.min_values = min_values
        self.max_values = max_values
        self.required = required
        self.file_types = list(file_types) if file_types is not None else None
        self.values = list(values) if values is not None else []

    def to_payload(self) -> dict[str, Any]:
        payload = {
            **self._base_payload(),
            "custom_id": self.custom_id,
            "min_values": self.min_values,
            "max_values": self.max_values,
            "required": self.required,
        }
        if self.file_types is not None:
            payload["file_types"] = list(self.file_types)
        return payload

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "FileUpload":
        return cls(
            payload["custom_id"],
            min_values=payload.get("min_values", 1),
            max_values=payload.get("max_values", 1),
            required=payload.get("required", True),
            file_types=payload.get("file_types"),
            values=payload.get("values"),
            id=payload.get("id"),
        )
