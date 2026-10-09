"""Button payload fields follow Discord button styles."""

from discord.ext import interaction


def test_premium_button_serializes_sku_id_as_snowflake():
    button = interaction.Button(style=6, sku_id=123456789)
    payload = button.to_dict()
    assert payload == {"type": 2, "style": 6, "sku_id": "123456789"}
    assert interaction.Button.from_dict(payload).to_dict() == {
        **payload, "disabled": False
    }
