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

import asyncio

import discord

from discord.state import ConnectionState
from discord.utils import MISSING
from typing import List, Union, Sequence, Optional

from .components import ActionRow, Button, Selection, from_payload
from .errors import InvalidArgument, AlreadyDeferred
from .http import handler_message_parameter
from .utils import deprecated


class Message(discord.Message):
    def __init__(
           self,
            *,
            state: ConnectionState,
            channel: Union[discord.TextChannel, discord.DMChannel, discord.GroupChannel],
            data: dict
    ):
        if "message_reference" in data and "channel_id" not in data.get("message_reference", {}):
            data["message_reference"]["channel_id"] = channel.id
        super().__init__(state=state, channel=channel, data=data)
        self.components = from_payload(data.get("components", []))

    async def send(
            self,
            content: Optional[str] = MISSING,
            *,
            tts: bool = False,
            embed: discord.Embed = MISSING,
            embeds: List[discord.Embed] = MISSING,
            file: Optional[discord.File] = MISSING,
            files: Optional[List[discord.File]] = MISSING,
            allowed_mentions: discord.AllowedMentions = MISSING,
            components: List[Union[ActionRow, Button, Selection]] = MISSING,
            reference: Union[discord.Message, discord.MessageReference, discord.PartialMessage] = MISSING,
            mention_author: bool = None,
            stickers: List[Union[discord.Sticker, int]] = MISSING,
            suppress_embeds: bool = False
    ):
        channel = MessageSendable(state=self._state, channel=self.channel)
        return await channel.send(
            content=content,
            tts=tts,
            embed=embed,
            embeds=embeds,
            file=file,
            files=files,
            allowed_mentions=allowed_mentions,
            components=components,
            reference=reference,
            mention_author=mention_author,
            stickers=stickers,
            suppress_embeds=suppress_embeds
        )

    async def edit(
            self,
            content: Optional[str] = MISSING,
            *,
            embed: discord.Embed = MISSING,
            embeds: List[discord.Embed] = MISSING,
            attachment: Union[discord.Attachment, discord.File] = MISSING,
            attachments: Sequence[Union[discord.Attachment, discord.File]] = MISSING,
            allowed_mentions: discord.AllowedMentions = MISSING,
            components: List[Union[ActionRow, Button, Selection]] = MISSING,
            stickers: List[discord.Sticker] = MISSING
    ):
        if attachment is not MISSING:
            if attachment is not MISSING and attachments is not MISSING:
                raise InvalidArgument()
            attachments = [attachment]
        params = handler_message_parameter(
            content=content, embed=embed, embeds=embeds,
            previous_allowed_mentions=self._state.allowed_mentions,
            attachments=attachments, allowed_mentions=allowed_mentions,
            components=components, stickers=stickers
        )

        await self._state.http.edit_message(
            channel_id=self.channel.id, message_id=self.id, params=params
        )
        return


@deprecated(version='0.1.2', reason='According to the recommendation to stop message command')
class MessageCommand(Message):
    def __init__(
            self,
            *,
            state: ConnectionState,
            channel: Union[discord.TextChannel, discord.DMChannel, discord.GroupChannel],
            data: dict
    ):
        super().__init__(state=state, channel=channel, data=data)
        options = self.content.split()

        if len(options) >= 1:
            self.name = options[0]
        else:
            self.name = None

        if len(options) >= 2:
            self.options = self.content.split()[1:]
        else:
            self.options = []

        self.deferred = False
        self.deferred_task: Optional[asyncio.Task] = None

    @staticmethod
    def _typing_done_callback(fut: asyncio.Future) -> None:
        # just retrieve any exception and call it a day
        try:
            fut.exception()
        except (asyncio.CancelledError, Exception):
            pass

    async def _do_deferred(self) -> None:
        for count in range(0, 300, 10):
            await super().channel.typing()
            if not self.deferred:
                break
            await asyncio.sleep(10)

    async def defer(
            self,
            _: bool = None
    ) -> None:
        if self.deferred:
            raise AlreadyDeferred()
        self.deferred = True
        self.deferred_task = self._state.loop.create_task(self._do_deferred())
        self.deferred_task.add_done_callback(self._typing_done_callback)
        return

    async def send(
            self,
            content=None,
            *,
            tts: bool = False,
            embed: discord.Embed = None,
            embeds: List[discord.Embed] = None,
            file: discord.File = None,
            files: List[discord.File] = None,
            allowed_mentions: discord.AllowedMentions = None,
            components: List[Union[ActionRow, Button, Selection]] = None,
            reference: Union[Message, discord.MessageReference, discord.PartialMessage] = MISSING,
            mention_author: bool = None,
            stickers: List[Union[discord.Sticker, int]] = MISSING,
            suppress_embeds: bool = False
    ) -> Optional[Message]:
        self.deferred = False
        if self.deferred_task is not None:
            if not self.deferred_task.cancelled():
                self.deferred_task.cancel()
        return await super().send(
            content=content,
            tts=tts,
            embed=embed,
            embeds=embeds,
            file=file,
            files=files,
            allowed_mentions=allowed_mentions,
            components=components,
            reference=reference,
            mention_author=mention_author,
            stickers=stickers,
            suppress_embeds=suppress_embeds
        )


class MessageSendable:
    def __init__(self, state: ConnectionState, channel):
        self._state = state
        self.channel = channel

    async def send(
            self,
            content: Optional[str] = MISSING,
            *,
            tts: bool = False,
            embed: discord.Embed = MISSING,
            embeds: Sequence[discord.Embed] = MISSING,
            file: discord.File = MISSING,
            files: List[discord.File] = MISSING,
            allowed_mentions: discord.AllowedMentions = MISSING,
            components: List[Union[ActionRow, Button, Selection]] = MISSING,
            reference: Union[Message, discord.MessageReference, discord.PartialMessage] = MISSING,
            mention_author: bool = None,
            stickers: List[Union[discord.Sticker, int]] = MISSING,
            suppress_embeds: bool = False
    ):
        if reference is not None:
            try:
                reference_dict = reference.to_message_reference_dict()
            except AttributeError:
                raise TypeError('reference parameter must be Message, MessageReference, or PartialMessage') from None
        else:
            reference_dict = MISSING

        if suppress_embeds:
            flags = discord.MessageFlags(suppress_embeds=suppress_embeds)
        else:
            flags = MISSING

        params = handler_message_parameter(
            content=content, tts=tts, embed=embed, embeds=embeds,
            previous_allowed_mentions=self._state.allowed_mentions,
            file=file, files=files, allowed_mentions=allowed_mentions, flags=flags,
            components=components, reference=reference_dict, mention_author=mention_author, stickers=stickers
        )

        resp = await self._state.http.send_message(params=params, channel_id=self.channel.id)
        ret = Message(state=self._state, channel=self.channel, data=resp)
        return ret
