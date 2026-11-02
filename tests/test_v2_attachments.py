"""V2 media references match files attached to the same payload."""

from io import BytesIO

import discord
import pytest

from discord.ext import interaction
from discord.ext.interaction.parser import handle_message_parameter


def test_file_component_reference_matches_multipart_upload():
    component = interaction.File(interaction.UnfurledMediaItem("attachment://report.txt"))
    upload = discord.File(BytesIO(b"report"), filename="report.txt")
    try:
        params = handle_message_parameter(components=[component], file=upload)
        assert params.payload is None
        assert [file.filename for file in params.files] == ["report.txt"]
        assert any(part["name"] == "payload_json" for part in params.multipart)
    finally:
        upload.close()


def test_missing_file_for_v2_media_reference_is_rejected():
    gallery = interaction.MediaGallery([
        interaction.MediaGalleryItem(
            interaction.UnfurledMediaItem("attachment://missing.png")
        )
    ])
    with pytest.raises(ValueError, match="missing file"):
        handle_message_parameter(components=[gallery])
