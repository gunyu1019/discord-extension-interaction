"""handle_message_parameter — component injection alongside file uploads."""
import io
import json

import discord
import pytest

from discord.ext.interaction.components import ActionRow, Button
from discord.ext.interaction.parser import handle_message_parameter


def _file():
    return discord.File(io.BytesIO(b"payload"), filename="a.txt")


def _row():
    return ActionRow(components=[Button(label="b", custom_id="c", style=1)])


def _payload_json(result):
    for part in result.multipart:
        if part["name"] == "payload_json":
            return json.loads(part["value"])
    raise AssertionError("no payload_json part")


def test_components_with_a_file_do_not_crash_and_land_in_multipart():
    result = handle_message_parameter(content="hi", file=_file(), components=[_row()])
    assert result.payload is None  # discord.py moved the body into multipart
    body = _payload_json(result)
    assert body["components"][0]["type"] == 1
    assert body["components"][0]["components"][0]["custom_id"] == "c"


def test_components_none_with_a_file_clears_components_without_crashing():
    result = handle_message_parameter(content="hi", file=_file(), components=None)
    assert result.payload is None
    assert _payload_json(result)["components"] == []


def test_components_missing_with_a_file_leaves_body_untouched():
    result = handle_message_parameter(content="hi", file=_file())
    assert "components" not in _payload_json(result)


def test_components_without_a_file_still_use_the_plain_payload():
    result = handle_message_parameter(content="hi", components=[_row()])
    assert result.payload is not None
    assert result.payload["components"][0]["type"] == 1
