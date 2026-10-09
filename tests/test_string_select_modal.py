"""The existing Selection API can render a modal String Select."""

from discord.ext import interaction


def test_modal_string_select_serializes_required_without_disabled():
    select = interaction.Selection(
        custom_id="pet", options=[interaction.SelectOption("Cat", "cat")],
        required=False,
    )
    label = interaction.Label(select, label="Pet")
    child = label.to_all_dict()["component"]
    assert child["required"] is False
    assert "disabled" not in child
    assert interaction.Selection.from_dict(select.to_dict()).required is False
