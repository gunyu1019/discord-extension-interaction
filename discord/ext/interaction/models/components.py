"""Discord component payload models and validation."""

from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Any, ClassVar

# Component


class Component(ABC):
    """A component with Discord's ``type`` and optional 32-bit ``id`` fields."""

    TYPE: ClassVar[int]

    def __init__(self, *, id: int | None = None):
        if id is not None and (type(id) is not int or not 0 <= id <= 0xFFFFFFFF):
            raise ValueError("component id must be a 32-bit unsigned integer")
        self.id = id

    @property
    def type(self) -> int:
        return self.TYPE

    def _base_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"type": self.type}
        if self.id is not None:
            payload["id"] = self.id
        return payload

    @abstractmethod
    def to_payload(self) -> dict[str, Any]:
        """Serialize this component to a Discord Component Object."""

    @classmethod
    @abstractmethod
    def from_payload(cls, payload: dict[str, Any]) -> "Component":
        """Restore this component from a Discord Component Object."""


# Select Default Value


class SelectDefaultValue:
    """A user, role, or channel selected when a menu first appears."""

    def __init__(self, id: int | str, type: str):
        if type not in ("user", "role", "channel"):
            raise ValueError("default value type must be user, role, or channel")
        if not str(id).isdigit() or int(id) <= 0:
            raise ValueError("default value id must be a snowflake")
        self.id = str(id)
        self.type = type

    def to_payload(self) -> dict[str, Any]:
        return {"id": self.id, "type": self.type}

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "SelectDefaultValue":
        return cls(payload["id"], payload["type"])


# Auto Select


class AutoSelect(Component):
    """Common fields for User, Role, Mentionable and Channel Selects."""

    DEFAULT_TYPES: tuple[str, ...] = ()

    def __init__(
        self,
        custom_id: str,
        *,
        placeholder: str | None = None,
        min_values: int | None = None,
        max_values: int | None = None,
        required: bool | None = None,
        disabled: bool | None = None,
        default_values: list[SelectDefaultValue] | None = None,
        values: list[str] | None = None,
        id: int | None = None,
    ):
        super().__init__(id=id)
        if not isinstance(custom_id, str) or not 1 <= len(custom_id) <= 100:
            raise ValueError("select custom_id requires 1 to 100 characters")
        if placeholder is not None and (
            not isinstance(placeholder, str) or len(placeholder) > 150
        ):
            raise ValueError("select placeholder exceeds 150 characters")
        minimum = 1 if min_values is None else min_values
        maximum = 1 if max_values is None else max_values
        if (
            type(minimum) is not int
            or type(maximum) is not int
            or not 0 <= minimum <= maximum <= 25
        ):
            raise ValueError("select min_values/max_values are invalid")
        if required is not None and type(required) is not bool:
            raise ValueError("select required must be a boolean")
        if disabled is not None and type(disabled) is not bool:
            raise ValueError("select disabled must be a boolean")
        if default_values is not None:
            if not all(isinstance(item, SelectDefaultValue) for item in default_values):
                raise TypeError(
                    "select default_values require SelectDefaultValue objects"
                )
            if not minimum <= len(default_values) <= maximum:
                raise ValueError(
                    "select default_values count is outside min_values/max_values"
                )
            if any(item.type not in self.DEFAULT_TYPES for item in default_values):
                raise ValueError(
                    "select default_values type is not allowed for this menu"
                )
        self.custom_id = custom_id
        self.placeholder = placeholder
        self.min_values = min_values
        self.max_values = max_values
        self.required = required
        self.disabled = disabled
        self.default_values = (
            list(default_values) if default_values is not None else None
        )
        self.values = list(values) if values is not None else []

    def to_payload(self) -> dict[str, Any]:
        payload = {**self._base_payload(), "custom_id": self.custom_id}
        for key in ("placeholder", "min_values", "max_values", "required", "disabled"):
            value = getattr(self, key)
            if value is not None:
                payload[key] = value
        if self.default_values is not None:
            payload["default_values"] = [
                item.to_payload() for item in self.default_values
            ]
        return payload

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "AutoSelect":
        return cls(
            payload["custom_id"],
            placeholder=payload.get("placeholder"),
            min_values=payload.get("min_values"),
            max_values=payload.get("max_values"),
            required=payload.get("required"),
            disabled=payload.get("disabled"),
            default_values=(
                [
                    SelectDefaultValue.from_payload(item)
                    for item in payload["default_values"]
                ]
                if "default_values" in payload
                else None
            ),
            values=payload.get("values"),
            id=payload.get("id"),
        )


# Channel Select


class ChannelSelect(AutoSelect):
    TYPE = 8
    DEFAULT_TYPES = ("channel",)

    def __init__(
        self, custom_id: str, *, channel_types: list[int] | None = None, **kwargs
    ):
        super().__init__(custom_id, **kwargs)
        normalized = [getattr(value, "value", value) for value in channel_types or ()]
        if channel_types is not None and not all(
            type(value) is int and value >= 0 for value in normalized
        ):
            raise ValueError(
                "Channel Select channel_types must be nonnegative integers"
            )
        self.channel_types = normalized if channel_types is not None else None

    def to_payload(self) -> dict[str, Any]:
        payload = super().to_payload()
        if self.channel_types is not None:
            payload["channel_types"] = list(self.channel_types)
        return payload

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "ChannelSelect":
        return cls(
            payload["custom_id"],
            channel_types=payload.get("channel_types"),
            placeholder=payload.get("placeholder"),
            min_values=payload.get("min_values"),
            max_values=payload.get("max_values"),
            required=payload.get("required"),
            disabled=payload.get("disabled"),
            default_values=(
                [
                    SelectDefaultValue.from_payload(item)
                    for item in payload["default_values"]
                ]
                if "default_values" in payload
                else None
            ),
            values=payload.get("values"),
            id=payload.get("id"),
        )


# Mentionable Select


class MentionableSelect(AutoSelect):
    TYPE = 7
    DEFAULT_TYPES = ("user", "role")


# Role Select


class RoleSelect(AutoSelect):
    TYPE = 6
    DEFAULT_TYPES = ("role",)


# User Select


class UserSelect(AutoSelect):
    TYPE = 5
    DEFAULT_TYPES = ("user",)


# Choice Group Option


class ChoiceGroupOption:
    """Value, label, optional description and default selection."""

    def __init__(
        self,
        value: str,
        label: str,
        *,
        description: str | None = None,
        default: bool | None = None,
    ):
        if not isinstance(value, str) or not 1 <= len(value) <= 100:
            raise ValueError("choice option value requires 1 to 100 characters")
        if not isinstance(label, str) or not 1 <= len(label) <= 100:
            raise ValueError("choice option label requires 1 to 100 characters")
        if description is not None and (
            not isinstance(description, str) or len(description) > 100
        ):
            raise ValueError("choice option description exceeds 100 characters")
        if default is not None and type(default) is not bool:
            raise ValueError("choice option default must be a boolean")
        self.value = value
        self.label = label
        self.description = description
        self.default = default

    def to_payload(self) -> dict[str, Any]:
        payload = {"value": self.value, "label": self.label}
        if self.description is not None:
            payload["description"] = self.description
        if self.default is not None:
            payload["default"] = self.default
        return payload

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "ChoiceGroupOption":
        return cls(
            payload["value"],
            payload["label"],
            description=payload.get("description"),
            default=payload.get("default"),
        )


# Checkbox


class Checkbox(Component):
    """A modal yes/no input whose submission carries a boolean value."""

    TYPE = 23

    def __init__(
        self,
        custom_id: str,
        *,
        default: bool | None = None,
        value: bool | None = None,
        id: int | None = None,
    ):
        super().__init__(id=id)
        if not isinstance(custom_id, str) or not 1 <= len(custom_id) <= 100:
            raise ValueError("Checkbox custom_id requires 1 to 100 characters")
        if default is not None and type(default) is not bool:
            raise ValueError("Checkbox default must be a boolean")
        if value is not None and type(value) is not bool:
            raise ValueError("Checkbox value must be a boolean")
        self.custom_id = custom_id
        self.default = default
        self.value = value

    def to_payload(self) -> dict[str, Any]:
        payload = {**self._base_payload(), "custom_id": self.custom_id}
        if self.default is not None:
            payload["default"] = self.default
        return payload

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "Checkbox":
        return cls(
            payload["custom_id"],
            default=payload.get("default"),
            value=payload.get("value"),
            id=payload.get("id"),
        )


# Checkbox Group


class CheckboxGroupOption(ChoiceGroupOption):
    """One Checkbox Group choice."""


class CheckboxGroup(Component):
    """A modal input that returns zero or more selected values."""

    TYPE = 22

    def __init__(
        self,
        custom_id: str,
        options: list[CheckboxGroupOption] | None = None,
        *,
        min_values: int | None = None,
        max_values: int | None = None,
        required: bool = True,
        values: list[str] | None = None,
        id: int | None = None,
    ):
        super().__init__(id=id)
        if not isinstance(custom_id, str) or not 1 <= len(custom_id) <= 100:
            raise ValueError("Checkbox Group custom_id requires 1 to 100 characters")
        if options is not None and (
            not 1 <= len(options) <= 10
            or not all(isinstance(option, CheckboxGroupOption) for option in options)
        ):
            raise ValueError("Checkbox Group requires 1 to 10 options")
        if type(required) is not bool:
            raise ValueError("Checkbox Group required must be a boolean")
        minimum = 1 if min_values is None else min_values
        maximum = (
            (len(options) if options is not None else 10)
            if max_values is None
            else max_values
        )
        if (
            type(minimum) is not int
            or type(maximum) is not int
            or not 0 <= minimum <= maximum <= 10
            or options is not None
            and maximum > len(options)
            or required
            and minimum == 0
        ):
            raise ValueError("Checkbox Group min_values/max_values are invalid")
        if (
            options is not None
            and sum(option.default is True for option in options) > maximum
        ):
            raise ValueError("Checkbox Group defaults exceed max_values")
        self.custom_id = custom_id
        self.options = list(options) if options is not None else None
        self.min_values = min_values
        self.max_values = max_values
        self.required = required
        self.values = list(values) if values is not None else []

    def to_payload(self) -> dict[str, Any]:
        payload = {**self._base_payload(), "custom_id": self.custom_id}
        if self.options is not None:
            payload["options"] = [option.to_payload() for option in self.options]
            if self.min_values is not None:
                payload["min_values"] = self.min_values
            if self.max_values is not None:
                payload["max_values"] = self.max_values
            payload["required"] = self.required
        return payload

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "CheckboxGroup":
        return cls(
            payload["custom_id"],
            options=(
                [
                    CheckboxGroupOption.from_payload(option)
                    for option in payload["options"]
                ]
                if "options" in payload
                else None
            ),
            min_values=payload.get("min_values"),
            max_values=payload.get("max_values"),
            required=payload.get("required", True),
            values=payload.get("values"),
            id=payload.get("id"),
        )


# Radio Group


class RadioGroupOption(ChoiceGroupOption):
    """One Radio Group choice."""


class RadioGroup(Component):
    """A modal input that returns one selected option value."""

    TYPE = 21

    def __init__(
        self,
        custom_id: str,
        options: list[RadioGroupOption] | None = None,
        *,
        required: bool = True,
        value: str | None = None,
        id: int | None = None,
    ):
        super().__init__(id=id)
        if not isinstance(custom_id, str) or not 1 <= len(custom_id) <= 100:
            raise ValueError("Radio Group custom_id requires 1 to 100 characters")
        if options is not None and (
            not 2 <= len(options) <= 10
            or not all(isinstance(option, RadioGroupOption) for option in options)
            or sum(option.default is True for option in options) > 1
        ):
            raise ValueError(
                "Radio Group requires 2 to 10 options and at most one default"
            )
        if type(required) is not bool:
            raise ValueError("Radio Group required must be a boolean")
        self.custom_id = custom_id
        self.options = list(options) if options is not None else None
        self.required = required
        self.value = value

    def to_payload(self) -> dict[str, Any]:
        payload = {**self._base_payload(), "custom_id": self.custom_id}
        if self.options is not None:
            payload["options"] = [option.to_payload() for option in self.options]
            payload["required"] = self.required
        return payload

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "RadioGroup":
        return cls(
            payload["custom_id"],
            options=(
                [RadioGroupOption.from_payload(option) for option in payload["options"]]
                if "options" in payload
                else None
            ),
            required=payload.get("required", True),
            value=payload.get("value"),
            id=payload.get("id"),
        )


# Text Display


class TextDisplay(Component):
    """Markdown text for a Components V2 message or a modal."""

    TYPE = 10

    def __init__(self, content: str, *, id: int | None = None):
        super().__init__(id=id)
        if not isinstance(content, str) or not content:
            raise ValueError("Text Display content must be a nonempty string")
        self.content = content

    def to_payload(self) -> dict[str, Any]:
        return {**self._base_payload(), "content": self.content}

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "TextDisplay":
        return cls(payload["content"], id=payload.get("id"))


# Separator


class Separator(Component):
    """Spacing or a divider in a Components V2 message."""

    TYPE = 14

    def __init__(
        self, *, divider: bool = True, spacing: int = 1, id: int | None = None
    ):
        super().__init__(id=id)
        if type(divider) is not bool:
            raise ValueError("Separator divider must be a boolean")
        if type(spacing) is not int or spacing not in (1, 2):
            raise ValueError("Separator spacing must be 1 or 2")
        self.divider = divider
        self.spacing = spacing

    def to_payload(self) -> dict[str, Any]:
        return {
            **self._base_payload(),
            "divider": self.divider,
            "spacing": self.spacing,
        }

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "Separator":
        return cls(
            divider=payload.get("divider", True),
            spacing=payload.get("spacing", 1),
            id=payload.get("id"),
        )


# Unfurled Media Item


class UnfurledMediaItem:
    """Media URL plus optional fields returned by Discord."""

    def __init__(self, url: str, *, response_fields: dict[str, Any] | None = None):
        if not isinstance(url, str) or not url:
            raise ValueError("Unfurled Media Item requires a URL")
        self.url = url
        self.response_fields = deepcopy(response_fields or {})

    def to_payload(self) -> dict[str, Any]:
        return {"url": self.url, **deepcopy(self.response_fields)}

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "UnfurledMediaItem":
        return cls(
            payload["url"],
            response_fields={
                key: value for key, value in payload.items() if key != "url"
            },
        )


# Thumbnail


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


# Media Gallery


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


# File Component


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


# File Upload


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


# Unknown Component


class UnknownComponent(Component):
    """Preserve every payload field of an unrecognized component type."""

    def __init__(self, payload: dict[str, Any]):
        component_type = payload["type"]
        if type(component_type) is not int or component_type <= 0:
            raise ValueError("component type must be a positive integer")
        super().__init__(id=payload.get("id"))
        self.TYPE = component_type
        self._payload = deepcopy(payload)

    @property
    def raw_payload(self) -> dict[str, Any]:
        return deepcopy(self._payload)

    def to_payload(self) -> dict[str, Any]:
        return deepcopy(self._payload)

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "UnknownComponent":
        return cls(payload)


# Section


class Section(Component):
    """One to three text components beside an accessory."""

    TYPE = 9

    def __init__(
        self,
        components: list[Component],
        accessory: Component,
        *,
        id: int | None = None,
    ):
        super().__init__(id=id)
        if not 1 <= len(components) <= 3:
            raise ValueError("Section requires 1 to 3 child components")
        if not all(isinstance(item, Component) for item in components):
            raise TypeError("Section children must be component models")
        if not isinstance(accessory, Component):
            raise TypeError("Section accessory must be a component model")
        self.components = list(components)
        self.accessory = accessory

    def to_payload(self) -> dict[str, Any]:
        return {
            **self._base_payload(),
            "components": [item.to_payload() for item in self.components],
            "accessory": self.accessory.to_payload(),
        }

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "Section":
        children = [
            (
                TextDisplay.from_payload(item)
                if item["type"] == 10
                else UnknownComponent.from_payload(item)
            )
            for item in payload["components"]
        ]
        return cls(
            children,
            (
                Thumbnail.from_payload(payload["accessory"])
                if payload["accessory"]["type"] == 11
                else UnknownComponent.from_payload(payload["accessory"])
            ),
            id=payload.get("id"),
        )


# Container

_KNOWN_CHILDREN = {
    Section.TYPE: Section,
    TextDisplay.TYPE: TextDisplay,
    Separator.TYPE: Separator,
    MediaGallery.TYPE: MediaGallery,
    File.TYPE: File,
}


class Container(Component):
    """Visual grouping of Components V2 message content."""

    TYPE = 17

    def __init__(
        self,
        components: list[Component],
        *,
        accent_color: int | None = None,
        spoiler: bool = False,
        id: int | None = None,
    ):
        super().__init__(id=id)
        if not components or not all(
            isinstance(item, Component) for item in components
        ):
            raise ValueError("Container requires component model children")
        if accent_color is not None and (
            type(accent_color) is not int or not 0 <= accent_color <= 0xFFFFFF
        ):
            raise ValueError("Container accent_color must be an RGB integer")
        if type(spoiler) is not bool:
            raise ValueError("Container spoiler must be a boolean")
        self.components = list(components)
        self.accent_color = accent_color
        self.spoiler = spoiler

    def to_payload(self) -> dict[str, Any]:
        payload = {
            **self._base_payload(),
            "components": [item.to_payload() for item in self.components],
            "spoiler": self.spoiler,
        }
        if self.accent_color is not None:
            payload["accent_color"] = self.accent_color
        return payload

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "Container":
        children = [
            _KNOWN_CHILDREN.get(item["type"], UnknownComponent).from_payload(item)
            for item in payload["components"]
        ]
        return cls(
            children,
            accent_color=payload.get("accent_color"),
            spoiler=payload.get("spoiler", False),
            id=payload.get("id"),
        )
