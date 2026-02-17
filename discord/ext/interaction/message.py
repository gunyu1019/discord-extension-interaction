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

import asyncio
from typing import TYPE_CHECKING
from collections.abc import Sequence

from discord.message import Message as OriginMessage
from discord.message import MessageFlags  # noqa
from discord.utils import MISSING

from .components import ActionRow, Button, Selection, from_payload
from .errors import InvalidArgument, AlreadyDeferred
from .parser import handle_message_parameter

if TYPE_CHECKING:
    from typing import Any, Optional, Union, List

    from discord.channel import TextChannel, DMChannel, GroupChannel
    from discord.embeds import Embed
    from discord.file import File
    from discord.sticker import Sticker
    from discord.mentions import AllowedMentions
    from discord.poll import Poll
    from discord.sticker import GuildSticker, StickerItem
    from discord.state import ConnectionState
    from discord.message import Attachment, MessageReference, PartialMessage


class Message(OriginMessage):
    """Represents a message from Discord for ``discord-extension-interaction``
    This depends on :class:`discord.Message`.

    Attributes
    ----------
    components: list[Component]
        A list of components in the message.
    """

    def __init__(
        self,
        *,
        state: ConnectionState,
        channel: TextChannel | DMChannel | GroupChannel,
        data: dict[str, Any]
    ):
        if "message_reference" in data and "channel_id" not in data.get(
            "message_reference", {}
        ):
            data["message_reference"]["channel_id"] = channel.id
        super().__init__(state=state, channel=channel, data=data)
        self.components = from_payload(data.get("components", []))

    async def send(
        self,
        content: Optional[str] = None,
        *,
        tts: bool = False,
        embed: Optional[Embed] = None,
        embeds: Optional[Sequence[Embed]] = None,
        file: Optional[File] = None,
        files: Optional[Sequence[File]] = None,
        stickers: Optional[Sequence[Union[GuildSticker, StickerItem]]] = None,
        delete_after: Optional[float] = None,
        nonce: Optional[Union[str, int]] = None,
        allowed_mentions: Optional[AllowedMentions] = None,
        reference: Optional[Union[Message, MessageReference, PartialMessage]] = None,
        mention_author: Optional[bool] = None,
        suppress_embeds: bool = False,
        silent: bool = False,
        poll: Optional[Poll] = None,
    ):
        channel = MessageTransferable(state=self._state, channel=self.channel)
        return await channel.send(
            content=content,
            tts=tts,
            embed=embed,
            embeds=embeds,
            file=file,
            files=files,
            allowed_mentions=allowed_mentions,
            # components=components,
            reference=reference,
            mention_author=mention_author,
            stickers=stickers,
            suppress_embeds=suppress_embeds,
        )

    async def edit(
        self,
        content: str | None = MISSING,
        *,
        embed: Embed = MISSING,
        embeds: list[Embed] = MISSING,
        attachment: Attachment | File = MISSING,
        attachments: Sequence[Attachment | File] = MISSING,
        allowed_mentions: AllowedMentions = MISSING,
        components: list[ActionRow | Button | Selection] = MISSING,
        stickers: list[Sticker] = MISSING
    ):
        message = MessageEditable(self.channel, self.id)
        return await message.edit(
            content=content,
            embed=embed,
            embeds=embeds,
            attachment=attachment,
            attachments=attachments,
            allowed_mentions=allowed_mentions,
            components=components,
            stickers=stickers,
        )


class MessageTransferable:
    """Use :class:`discord.Message` in ``discord-extension-interaction`` to send a message.
    Usage is the same as ``send()`` in :class:`discord.Message`.
    It can use the :class:`Components` in ``discord-extension-interaction``.

    Examples
    ---------
    @client.event
    async def on_message(message):
        state = getattr(client, "_connection")  # For private attributes
        message_send = interaction.MessageSendable(state, message.channel)
        await message_send.send("Hello World")
    """

    def __init__(self, state: ConnectionState, channel):
        self._state = state
        self.channel = channel

    async def send(
        self,
        content: str | None = MISSING,
        *,
        tts: bool = False,
        embed: Embed = MISSING,
        embeds: Sequence[Embed] = MISSING,
        file: File = MISSING,
        files: list[File] = MISSING,
        allowed_mentions: AllowedMentions = MISSING,
        components: list[ActionRow | Button | Selection] = MISSING,
        reference: Message | MessageReference | PartialMessage = None,
        mention_author: bool = None,
        stickers: list[Sticker | int] = MISSING,
        suppress_embeds: bool = False
    ):
        if reference is not None:
            try:
                reference_dict = reference.to_message_reference_dict()
            except AttributeError:
                raise TypeError(
                    "reference parameter must be Message, MessageReference, or PartialMessage"
                ) from None
        else:
            reference_dict = MISSING

        if suppress_embeds:
            flags = MessageFlags(suppress_embeds=suppress_embeds)
        else:
            flags = MISSING

        params = handle_message_parameter(
            content=content,
            tts=tts,
            embed=embed,
            embeds=embeds,
            previous_allowed_mentions=self._state.allowed_mentions,
            file=file,
            files=files,
            allowed_mentions=allowed_mentions,
            flags=flags,
            components=components,
            mention_author=mention_author,
            stickers=stickers,
        )

        resp = await self._state.http.send_message(
            params=params, channel_id=self.channel.id
        )
        ret = Message(state=self._state, channel=self.channel, data=resp)
        return ret


class MessageEditable:
    """Use :class:`discord.Message` in ``discord-extension-interaction`` to edit a message.
    Usage is the same as ``edit()`` in :class:`discord.Message`.
    It can use the :class:`Components` in ``discord-extension-interaction``.

    Examples
    ---------
    @client.event
    async def on_message(message):
        state = getattr(client, "_connection")  # For private attributes
        message_send = interaction.MessageEditable(message.channel, message.id)
        await message_send.edit("Hello World")
    """

    def __init__(self, channel, message_id: int):
        self.id = message_id
        self.channel = channel
        self._state = getattr(channel, "_state")

    async def edit(
        self,
        content: str | None = MISSING,
        *,
        embed: Embed = MISSING,
        embeds: list[Embed] = MISSING,
        attachment: Attachment | File = MISSING,
        attachments: Sequence[Attachment | File] = MISSING,
        allowed_mentions: AllowedMentions = MISSING,
        components: list[ActionRow | Button | Selection] = MISSING,
        stickers: list[Sticker] = MISSING
    ):
        if attachment is not MISSING:
            if attachment is not MISSING and attachments is not MISSING:
                raise InvalidArgument()
            attachments = [attachment]
        params = handle_message_parameter(
            content=content,
            embed=embed,
            embeds=embeds,
            previous_allowed_mentions=self._state.allowed_mentions,
            attachments=attachments,
            allowed_mentions=allowed_mentions,
            components=components,
            stickers=stickers,
        )

        await self._state.http.edit_message(
            channel_id=self.channel.id, message_id=self.id, params=params
        )
        return
