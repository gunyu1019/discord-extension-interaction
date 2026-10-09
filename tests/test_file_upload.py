"""File Upload supports modal filtering and submission IDs."""

import pytest

from discord.ext import interaction
from discord.ext.interaction.components import from_payload


def test_file_upload_modal_label_round_trip():
    upload = interaction.FileUpload(
        "files", min_values=0, max_values=2, required=False,
        file_types=["image", ".pdf"],
    )
    label = interaction.Label(upload, label="Files")
    payload = label.to_all_dict()
    assert payload["component"]["file_types"] == ["image", ".pdf"]
    assert isinstance(from_payload([payload])[0].component, interaction.FileUpload)


def test_file_upload_rejects_invalid_filters_and_bounds():
    with pytest.raises(ValueError, match="file_types"):
        interaction.FileUpload("files", file_types=["pdf"])
    with pytest.raises(ValueError, match="min_values"):
        interaction.FileUpload("files", min_values=0, required=True)
