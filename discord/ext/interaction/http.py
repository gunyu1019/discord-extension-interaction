"""MIT License

Copyright (c) 2021 gunyu1019

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import discord
from discord.http import Route
from discord.utils import MISSING
from typing import Any, NamedTuple
from collections.abc import Sequence


from .components import ActionRow, Button, Selection
from .utils import to_json


class MultipartParameters(NamedTuple):
    payload: dict[str, Any] | None
    multipart: list[dict[str, Any]] | None
    files: Sequence[discord.File] | None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        if self.files:
            for file in self.files:
                file.close()


def handler_message_parameter(
    content: str | None = MISSING,
    *,
    tts: bool = False,
    embed: discord.Embed = MISSING,
    embeds: Sequence[discord.Embed] = MISSING,
    nonce: int | str | None = None,
    flags: discord.MessageFlags = MISSING,
    file: discord.File = MISSING,
    files: Sequence[discord.File] = MISSING,
    allowed_mentions: discord.AllowedMentions = MISSING,
    attachments: Sequence[discord.Attachment | discord.File] = MISSING,
    components: list[ActionRow | Button | Selection] = MISSING,
    reference: discord.MessageReference | discord.PartialMessage = MISSING,
    previous_allowed_mentions: discord.AllowedMentions | None = None,
    mention_author: bool = None,
    stickers: list[discord.Sticker | int] = MISSING,
):
    if files is not MISSING and file is not MISSING:
        raise TypeError("Cannot mix file and files keyword arguments.")
    if embeds is not MISSING and embed is not MISSING:
        raise TypeError("Cannot mix embed and embeds keyword arguments.")

    if file is not MISSING:
        files = [file]

    payload = {"tts": tts}
    if embeds is not MISSING:
        if len(embeds) > 10:
            raise ValueError("embeds has a maximum of 10 elements.")
        payload["embeds"] = [e.to_dict() for e in embeds]

    if embed is not MISSING:
        if embed is None:
            payload["embeds"] = []
        else:
            payload["embeds"] = [embed.to_dict()]

    if content is not MISSING:
        if content is not None:
            payload["content"] = str(content)
        else:
            payload["content"] = None

    if components is not MISSING:
        if components is not None:
            payload["components"] = [
                i.to_all_dict() if isinstance(i, ActionRow) else i.to_dict()
                for i in components
            ]
        else:
            payload["components"] = []

    if nonce is not None:
        payload["nonce"] = str(nonce)

    if reference is not MISSING:
        payload["message_reference"] = reference

    if stickers is not MISSING:
        if stickers is not None:
            payload["sticker_ids"] = [
                sticker.id if isinstance(stickers, discord.Sticker) else stickers
                for sticker in stickers
            ]
        else:
            payload["sticker_ids"] = []

    if flags is not MISSING:
        payload["flags"] = flags.value

    if allowed_mentions:
        if previous_allowed_mentions is not None:
            payload["allowed_mentions"] = previous_allowed_mentions.merge(
                allowed_mentions
            ).to_dict()
        else:
            payload["allowed_mentions"] = allowed_mentions.to_dict()
    elif previous_allowed_mentions is not None:
        payload["allowed_mentions"] = previous_allowed_mentions.to_dict()

    if mention_author is not None:
        if "allowed_mentions" not in payload:
            payload["allowed_mentions"] = discord.AllowedMentions().to_dict()
        payload["allowed_mentions"]["replied_user"] = mention_author

    if attachments is MISSING:
        attachments = files
    else:
        files = [a for a in attachments if isinstance(a, discord.File)]

    if attachments is not MISSING:
        file_index = 0
        attachments_payload = []
        for attachment in attachments:
            if isinstance(attachment, discord.File):
                attachments_payload.append(attachment.to_dict(file_index))
                file_index += 1
            else:
                attachments_payload.append(attachment.to_dict(file_index))

        payload["attachments"] = attachments_payload

    multipart = []
    if files:
        multipart.append({"name": "payload_json", "value": to_json(payload)})
        payload = None
        for index, file in enumerate(files):
            multipart.append(
                {
                    "name": f"files[{index}]",
                    "value": file.fp,
                    "filename": file.filename,
                    "content_type": "application/octet-stream",
                }
            )

    return MultipartParameters(payload=payload, multipart=multipart, files=files)


class InteractionData(NamedTuple):
    id: int
    application_id: str
    token: str


class InteractionHTTPClient:
    def __init__(self, http: discord.http.HTTPClient):
        self.http = http

    # Interaction Response
    async def post_initial_response(
        self, data: InteractionData, payload: dict[str, Any]
    ):
        r = Route(
            "POST", "/interactions/{id}/{token}/callback", id=data.id, token=data.token
        )
        return await self.http.request(r, json=payload)

    async def get_initial_response(self, data: InteractionData):
        r = Route(
            "GET",
            "/webhooks/{id}/{token}/messages/@original",
            id=data.application_id,
            token=data.token,
        )
        return await self.http.request(r)

    async def edit_initial_response(
        self,
        data: InteractionData,
        payload: dict[str, Any] = None,
        form: list[dict[str, Any]] = None,
        files: Sequence[discord.File] | None = MISSING,
    ):
        if form is None:
            form = []

        if len(form) > 0:
            return await self.edit_followup(
                message_id="@original", form=form, files=files, data=data
            )
        return await self.edit_followup(
            message_id="@original", payload=payload, data=data
        )

    async def delete_initial_response(self, data: InteractionData):
        await self.delete_followup(message_id="@original", data=data)

    # Interaction Response (Followup)
    async def post_followup(
        self,
        data: InteractionData,
        payload: dict[str, Any] = None,
        form: list[dict[str, Any]] = None,
        files: Sequence[discord.File] | None = MISSING,
    ):
        if form is None:
            form = []
        r = Route(
            "POST", "/webhooks/{id}/{token}", id=data.application_id, token=data.token
        )
        if len(form) > 0:
            return await self.http.request(r, form=form, files=files)
        return await self.http.request(r, json=payload)

    async def edit_followup(
        self,
        data: InteractionData,
        message_id,
        payload: dict[str, Any] = None,
        form: list[dict[str, Any]] = None,
        files: Sequence[discord.File] | None = MISSING,
    ):
        if form is None:
            form = []
        r = Route(
            "PATCH",
            "/webhooks/{id}/{token}/messages/{message_id}",
            id=data.application_id,
            token=data.token,
            message_id=message_id,
        )
        if len(form) > 0:
            return await self.http.request(r, form=form, files=files)
        return await self.http.request(r, json=payload)

    async def delete_followup(self, data: InteractionData, message_id):
        r = Route(
            "DELETE",
            "/webhooks/{id}/{token}/messages/{message_id}",
            id=data.application_id,
            token=data.token,
            message_id=message_id,
        )
        await self.http.request(r)
