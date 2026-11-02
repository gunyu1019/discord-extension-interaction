"""File components refer only to uploaded attachments."""

import pytest

from discord.ext import interaction


def test_file_component_round_trip_in_container():
    media = interaction.UnfurledMediaItem("attachment://report.pdf")
    file = interaction.File(media, name="report.pdf", size=1234, id=7)
    container = interaction.Container([file])
    restored = interaction.Container.from_payload(container.to_payload())
    assert restored.to_payload() == container.to_payload()
    assert isinstance(restored.components[0], interaction.File)


def test_file_component_rejects_remote_media():
    with pytest.raises(ValueError, match="attachment://"):
        interaction.File(
            interaction.UnfurledMediaItem("https://example.com/report.pdf")
        )


def test_file_component_parses_discord_cdn_response_without_allowing_resend():
    from discord.ext.interaction.parser import handle_message_parameter

    payload = {
        "type": 13,
        "file": {
            "url": "https://cdn.discordapp.com/attachments/1/2/report.pdf",
            "attachment_id": "2",
        },
        "name": "report.pdf",
        "size": 1234,
    }
    received = interaction.File.from_payload(payload)
    assert received.to_payload() == {**payload, "spoiler": False}
    with pytest.raises(ValueError, match="attachment://"):
        handle_message_parameter(components=[received])
