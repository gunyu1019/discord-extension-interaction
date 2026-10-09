"""Message ActionRows reject invalid Discord component arrangements."""

import asyncio

import pytest

from discord.ext import interaction
from discord.ext.interaction.application.component_validation import (
    validate_modal_components,
    validate_modal_container,
)
from discord.ext.interaction.parser import handle_message_parameter


def _button(index):
    return interaction.Button(style=1, label=str(index), custom_id=f"button-{index}")


def test_message_action_row_accepts_buttons_or_one_select():
    buttons = interaction.ActionRow([_button(1), _button(2)])
    select = interaction.ActionRow([
        interaction.Selection(
            custom_id="pick", options=[interaction.SelectOption("A", "a")]
        )
    ])

    assert handle_message_parameter(content="hello", components=[buttons]).payload[
        "components"
    ][0]["type"] == 1
    assert handle_message_parameter(content="hello", components=[select]).payload[
        "components"
    ][0]["components"][0]["type"] == 3


@pytest.mark.parametrize(
    "component",
    [
        _button(7),
        interaction.Selection("pick", [interaction.SelectOption("A", "a")]),
    ],
)
def test_legacy_single_component_is_wrapped_without_mutation(component):
    supplied = [component]
    payload = handle_message_parameter(content="hello", components=supplied).payload
    assert payload["components"][0]["type"] == 1
    assert payload["components"][0]["components"][0]["type"] == component.TYPE
    assert supplied == [component]


def test_message_rejects_duplicate_custom_ids_across_rows():
    with pytest.raises(ValueError, match="duplicate.*custom_id"):
        handle_message_parameter(
            content="hello",
            components=[interaction.ActionRow([_button(1)]), _button(1)],
        )


def test_legacy_message_rejects_more_than_five_rows():
    with pytest.raises(ValueError, match="at most 5"):
        handle_message_parameter(content="hello", components=[_button(i) for i in range(6)])


@pytest.mark.parametrize(
    "component",
    [interaction.Label(interaction.TextInput(custom_id="x", style=1), label="X"),
     interaction.TextInput(custom_id="x", style=1)],
)
def test_message_rejects_modal_only_top_level_components(component):
    with pytest.raises(ValueError, match="top-level ActionRows"):
        handle_message_parameter(content="hello", components=[component])


@pytest.mark.parametrize(
    "children",
    [
        [],
        [_button(index) for index in range(6)],
        [_button(1), interaction.Selection("pick", [])],
        [interaction.ActionRow([_button(1)])],
    ],
)
def test_message_action_row_rejects_invalid_children(children):
    with pytest.raises(ValueError, match="ActionRow"):
        handle_message_parameter(
            content="hello", components=[interaction.ActionRow(children)]
        )


def test_modal_accepts_label_and_legacy_text_input_row():
    text_input = interaction.TextInput(custom_id="name", style=1)
    validate_modal_container(interaction.Label(text_input, label="Name"))
    validate_modal_container(interaction.ActionRow([text_input]))


@pytest.mark.parametrize(
    "container",
    [
        interaction.Label(interaction.Button(style=1, label="Go", custom_id="go"), label="Go"),
        interaction.Label(interaction.TextInput(custom_id="x", style=1)),
        interaction.ActionRow([]),
        interaction.ActionRow([interaction.TextInput(custom_id="x", style=1)] * 2),
        interaction.ActionRow([interaction.Button(style=1, label="Go", custom_id="go")]),
    ],
)
def test_modal_rejects_invalid_container(container):
    with pytest.raises(ValueError, match="modal"):
        validate_modal_container(container)


def test_modal_rejects_duplicate_custom_ids_and_message_components():
    with pytest.raises(ValueError, match="duplicate.*custom_id"):
        validate_modal_components([
            interaction.Label(interaction.TextInput(custom_id="x", style=1), label="One"),
            interaction.ActionRow([interaction.TextInput(custom_id="x", style=1)]),
        ])
    with pytest.raises(ValueError, match="top-level"):
        validate_modal_components([_button(1)])


def test_invalid_modal_does_not_consume_response(offline_client, user_payload):
    payload = {
        "id": "40", "application_id": "20", "type": 2, "token": "tk",
        "version": 1, "user": user_payload, "channel_id": "30",
        "data": {"id": "50", "name": "open", "type": 1},
    }
    context = interaction.ApplicationContext(payload, offline_client)
    with pytest.raises(ValueError, match="modal"):
        asyncio.run(context.modal("m1", "Title", [interaction.ActionRow([])]))
    assert not context.responded
