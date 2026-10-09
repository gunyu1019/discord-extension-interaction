"""Separator fields use Discord's divider and spacing values."""

import pytest

from discord.ext import interaction


def test_separator_round_trip_and_defaults():
    payload = {"type": 14, "id": 9, "divider": False, "spacing": 2}
    assert interaction.Separator.from_payload(payload).to_payload() == payload
    assert interaction.Separator().to_payload() == {
        "type": 14, "divider": True, "spacing": 1
    }


@pytest.mark.parametrize("spacing", [0, 3, True])
def test_separator_rejects_invalid_spacing(spacing):
    with pytest.raises(ValueError, match="spacing"):
        interaction.Separator(spacing=spacing)
