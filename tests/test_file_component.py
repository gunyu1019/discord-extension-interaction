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
        interaction.File(interaction.UnfurledMediaItem("https://example.com/report.pdf"))
