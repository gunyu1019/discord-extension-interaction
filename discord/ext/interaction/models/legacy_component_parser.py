"""Parse the existing component types without changing their public classes."""

from typing import Any

from discord.ext.interaction.models.components import UnknownComponent
from discord.ext.interaction.models.component_codec import (
    parse_component_model,
)
from discord.ext.interaction.models.legacy_action_row import ActionRow
from discord.ext.interaction.models.legacy_button import Button
from discord.ext.interaction.models.legacy_label import Label
from discord.ext.interaction.models.legacy_selection import Selection
from discord.ext.interaction.models.legacy_text_input import TextInput


def from_payload(
    payload: list[dict[str, Any]],
) -> list[ActionRow | Button | Selection | TextInput | Label | UnknownComponent]:
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
        elif item.get("type") in (
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13,
            14,
            17,
            19,
            21,
            22,
            23,
        ):
            components.append(parse_component_model(item))
        else:
            components.append(UnknownComponent.from_payload(item))
    return components
