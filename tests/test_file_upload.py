"""File Upload supports modal filtering and submission IDs."""

import pytest
import discord

from discord.ext import interaction
from discord.ext.interaction.implementation.components import from_payload


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


def test_file_upload_submission_resolves_attachments(offline_client, user_payload):
    attachment = {
        "id": "900", "filename": "report.pdf", "size": 3,
        "url": "https://cdn.discordapp.com/report.pdf",
        "proxy_url": "https://media.discordapp.net/report.pdf",
    }
    payload = {
        "id": "40", "application_id": "20", "type": 5, "token": "tk",
        "version": 1, "user": user_payload, "channel_id": "30",
        "data": {
            "custom_id": "survey",
            "components": [{"type": 18, "component": {
                "type": 19, "custom_id": "files", "values": ["900"],
            }}],
            "resolved": {"attachments": {"900": attachment}},
        },
    }
    context = interaction.ModalSubmitContext(payload, offline_client)
    assert context.components[0].values == ["900"]
    assert isinstance(context.file_uploads["files"][0], discord.Attachment)
    assert context.file_uploads["files"][0].filename == "report.pdf"
