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
from __future__ import annotations

from discord.http import handle_message_parameters as origin_handle_message_parameter
from discord.webhook.async_ import interaction_message_response_params, interaction_response_params  # noqa
from discord.utils import MISSING
from typing import TYPE_CHECKING
from collections.abc import Sequence


from .components import ActionRow, Button, Selection

if TYPE_CHECKING:
    from discord import Attachment, MessageFlags
    from discord.embeds import Embed
    from discord.file import File
    from discord.flags import MessageFlags
    from discord.mentions import AllowedMentions
    from discord.message import MessageReference
    from discord.http import MultipartParameters
    from discord.types.snowflake import SnowflakeList
    from discord.poll import Poll
    from typing import Any, Optional, Union, Dict


def handle_message_parameter(
    content: str | None = MISSING,
    *,
    username: str = MISSING,
    avatar_url: Any = MISSING,
    tts: bool = False,
    nonce: Optional[Union[int, str]] = None,
    flags: MessageFlags = MISSING,
    file: File = MISSING,
    files: Sequence[File] = MISSING,
    embed: Optional[Embed] = MISSING,
    embeds: Sequence[Embed] = MISSING,
    attachments: Sequence[Union[Attachment, File]] = MISSING,
    # view: Optional[BaseView] = MISSING,
    allowed_mentions: Optional[AllowedMentions] = MISSING,
    message_reference: Optional[MessageReference] = MISSING,
    stickers: Optional[SnowflakeList] = MISSING,
    previous_allowed_mentions: Optional[AllowedMentions] = None,
    mention_author: Optional[bool] = None,
    thread_name: str = MISSING,
    channel_payload: Dict[str, Any] = MISSING,
    applied_tags: Optional[SnowflakeList] = MISSING,
    poll: Optional[Poll] = MISSING,
    components: list[ActionRow | Button | Selection] = MISSING,
) -> MultipartParameters:
    result = origin_handle_message_parameter(
        content=content,
        username=username,
        avatar_url=avatar_url,
        tts=tts,
        nonce =nonce,
        flags=flags,
        file=file,
        files=files,
        embed=embed,
        embeds=embeds,
        attachments =attachments ,
        allowed_mentions=allowed_mentions,
        message_reference=message_reference,
        stickers=stickers,
        previous_allowed_mentions=previous_allowed_mentions,
        mention_author=mention_author,
        thread_name=thread_name,
        channel_payload=channel_payload,
        applied_tags=applied_tags,
        poll=poll,
    )

    if components is not MISSING:
        if components is not None:
            result.payload["components"] = [
                i.to_all_dict() if isinstance(i, ActionRow) else i.to_dict()
                for i in components
            ]
        else:
            result.payload["components"] = []

    return result


def handle_interaction_response_parameter(
        interaction_type: int,
        data: Optional[Dict[str, Any]] = None
) -> MultipartParameters:
    return interaction_response_params(type=interaction_type, data=data)


def handle_interaction_message_parameter(
    *,
    interaction_type: int,
    content: Optional[str] = MISSING,
    tts: bool = False,
    flags: MessageFlags = MISSING,
    file: File = MISSING,
    files: Sequence[File] = MISSING,
    embed: Optional[Embed] = MISSING,
    embeds: Sequence[Embed] = MISSING,
    attachments: Sequence[Union[Attachment, File]] = MISSING,
    allowed_mentions: Optional[AllowedMentions] = MISSING,
    previous_allowed_mentions: Optional[AllowedMentions] = None,
    poll: Poll = MISSING,
    components: list[ActionRow | Button | Selection] = MISSING,
) -> MultipartParameters:
    result = interaction_message_response_params(
        type=interaction_type,
        content=content,
        tts=tts,
        flags=flags,
        file=file,
        files=files,
        embed=embed,
        embeds=embeds,
        attachments=attachments,
        allowed_mentions=allowed_mentions,
        previous_allowed_mentions=previous_allowed_mentions,
        poll=poll,
    )

    if components is not MISSING:
        if components is not None:
            result.payload["components"] = [
                i.to_all_dict() if isinstance(i, ActionRow) else i.to_dict()
                for i in components
            ]
        else:
            result.payload["components"] = []

    return result
