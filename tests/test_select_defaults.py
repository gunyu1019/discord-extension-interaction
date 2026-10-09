"""Auto-select defaults use Discord's snowflake/type objects."""

import pytest

from discord.ext import interaction


def test_mentionable_defaults_round_trip():
    select = interaction.MentionableSelect(
        "people", max_values=2,
        default_values=[
            interaction.SelectDefaultValue(10, "user"),
            interaction.SelectDefaultValue("20", "role"),
        ],
    )
    payload = select.to_payload()
    assert payload["default_values"] == [
        {"id": "10", "type": "user"}, {"id": "20", "type": "role"}
    ]
    assert interaction.MentionableSelect.from_payload(payload).to_payload() == payload


def test_auto_select_rejects_wrong_default_type_or_count():
    with pytest.raises(ValueError, match="type"):
        interaction.UserSelect("people", default_values=[interaction.SelectDefaultValue(10, "role")])
    with pytest.raises(ValueError, match="count"):
        interaction.RoleSelect("roles", default_values=[
            interaction.SelectDefaultValue(10, "role"),
            interaction.SelectDefaultValue(20, "role"),
        ])
