"""Parse the existing component types without changing their public classes."""

from typing import Any

from .action_row import ActionRow
from .button import Button
from .label import Label
from .selection import Selection
from .text_input import TextInput


def from_payload(
    payload: list[dict[str, Any]],
) -> list[ActionRow | Button | Selection | TextInput | Label]:
    components = []

    for item in payload:
        if item.get("type") == 1:
            components.append(ActionRow.from_payload(item))
        elif item.get("type") == 2:
            components.append(Button.from_dict(item))
        elif item.get("type") == 3:
            components.append(Selection.from_dict(item))
        elif item.get("type") == 4:
            components.append(TextInput.from_dict(item))
        elif item.get("type") == 18:
            components.append(Label.from_payload(item))
    return components
