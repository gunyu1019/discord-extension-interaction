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

import logging
from typing import Optional, List, Union

import discord
from discord.state import ConnectionState

from .commands import CommandOptionChoice
from .components import ActionRow, Button, Selection, Components, from_payload
from .errors import InvalidArgument, AlreadyDeferred
from .http import HttpClient, InteractionData
from .message import Message
from .utils import get_as_snowflake, _files_to_form, _allowed_mentions, channel_types

log = logging.getLogger()


class PartialMessageable:
    def __init__(self, state: ConnectionState, id: int, type: Optional[discord.ChannelType] = None):
        self._state: ConnectionState = state
        self._channel: discord.Object = discord.Object(id=id)
        self.id: int = id
        self.type: Optional[discord.ChannelType] = type

    async def _get_channel(self) -> discord.Object:
        return self._channel


class InteractionContext:
    def __init__(self, payload: dict, client):
        self.client = client
        self.id: int = get_as_snowflake(payload, "id")
        self.version = payload.get("version")
        self.type = payload.get("type")
        self.token = payload.get("token")
        self.application = get_as_snowflake(payload, "application_id")

        self._state: ConnectionState = getattr(client, "_connection")

        self.guild_id = payload.get("guild_id")
        self.channel_id = payload.get("channel_id")

        if self.guild is not None:
            member = payload.get("member")
            self.author = discord.Member(data=member, state=self._state, guild=self.guild)
        else:
            user = payload.get("user")
            self.author = discord.User(data=user, state=self._state)
        self.created_at = discord.utils.snowflake_time(self.id)
        self.locale = payload.get('locale')
        self.guild_locale = payload.get('guild_locale')

        self.deferred = False
        self.responded = False

        self.data = InteractionData(
            interaction_token=self.token,
            interaction_id=self.id,
            application_id=self.application
        )
        if hasattr(self.client, "interaction_http"):
            self.http = self.client.interaction_http
        else:
            self.http = HttpClient(http=self.client.http)

    @classmethod
    def from_original_data(cls, response, client, _cls=None):
        if _cls is not None:
            new_cls = _cls({}, client)
        else:
            new_cls = cls({}, client)
        new_cls.application = response.application_id
        new_cls.id = response.id
        new_cls.created_at = discord.utils.snowflake_time(new_cls.id)
        new_cls.type = response.type
        new_cls.token = response.token
        new_cls.version = response.version

        new_cls.guild_id = response.guild_id
        new_cls.channel_id = response.channel_id
        new_cls.locale = getattr(response, 'locale', None)
        new_cls.guild_locale = getattr(response, 'guild_locale', None)
        new_cls.author = response.user

        new_cls.data = InteractionData(
            interaction_token=new_cls.token,
            interaction_id=new_cls.id,
            application_id=new_cls.application
        )

        return new_cls

    @property
    def guild(self) -> Optional[discord.Guild]:
        if self.guild_id is not None:
            return self.client.get_guild(int(self.guild_id))
        return

    @property
    def channel(self) -> Optional:
        if self.channel_id is not None:
            if self.guild is not None:
                channel = self.guild.get_channel(int(self.channel_id))
            else:
                tp = discord.ChannelType.text if self.guild_id is not None else discord.ChannelType.private
                channel = PartialMessageable(state=self._state, id=self.channel_id, type=tp)
            return channel
        return

    @staticmethod
    def _get_payload(
            content=None,
            tts: bool = False,
            embed=None,
            hidden: bool = False,
            allowed_mentions=None,
            components=None
    ) -> dict:

        payload = {}
        if content:
            payload['content'] = content
        if tts:
            payload['tts'] = tts
        if embed:
            payload['embeds'] = embed
        if allowed_mentions:
            payload['allowed_mentions'] = allowed_mentions
        if hidden:
            payload['flags'] = 1 << 6
        if components:
            payload['components'] = components
        return payload

    @property
    def voice_client(self) -> Optional[discord.VoiceClient]:
        if self.guild is None:
            return None
        return self.guild.voice_client

    async def defer(self, hidden: bool = False):
        if self.deferred:
            raise AlreadyDeferred

        base = {"type": 5}
        if hidden:
            base["data"] = {"flags": 64}

        await self.http.post_initial_response(payload=base, data=self.data)
        self.deferred = True
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
            hidden: bool = False,
            allowed_mentions: discord.AllowedMentions = None,
            components: List[Union[ActionRow, Button, Selection]] = None
    ):
        if file is not None and files is not None:
            raise InvalidArgument()
        if embed is not None and embeds is not None:
            raise InvalidArgument()

        content = str(content) if content is not None else None
        if embed is not None:
            embeds = [embed]
        if embeds is not None:
            embeds = [embed.to_dict() for embed in embeds]
        if file:
            files = [file]
        if components is not None:
            components = [i.to_all_dict() if isinstance(i, ActionRow) else i.to_dict() for i in components]

        allowed_mentions = _allowed_mentions(self._state, allowed_mentions)
        payload = self._get_payload(
            content=content,
            embed=embeds,
            tts=tts,
            hidden=hidden,
            allowed_mentions=allowed_mentions,
            components=components,
        )

        if files:
            form = _files_to_form(files=files, payload=payload)
        else:
            form = None

        if not self.responded:
            if files and not self.deferred:
                await self.defer(hidden=hidden)

            if self.deferred:
                resp = await self.http.edit_initial_response(payload=payload, form=form, files=files, data=self.data)
                self.deferred = False
            else:
                await self.http.post_initial_response(
                    payload={
                        "type": 4,
                        "data": payload
                    },
                    data=self.data
                )
                resp = await self.http.get_initial_response(data=self.data)
            self.responded = True
        else:
            resp = await self.http.post_followup(payload=payload, form=form, files=files, data=self.data)
        ret = Message(state=self._state, channel=self.channel, data=resp)

        if files:
            for i in files:
                i.close()
        return ret

    async def edit(
            self,
            message_id="@original",
            content=None,
            *,
            embed: discord.Embed = None,
            embeds: List[discord.Embed] = None,
            file: discord.File = None,
            files: List[discord.File] = None,
            allowed_mentions: discord.AllowedMentions = None,
            components: List[Union[ActionRow, Button, Selection]] = None
    ):
        if file is not None and files is not None:
            raise InvalidArgument()
        if embed is not None and embeds is not None:
            raise InvalidArgument()

        content = str(content) if content is not None else None
        if embed is not None:
            embeds = [embed]
        if embeds is not None:
            embeds = [embed.to_dict() for embed in embeds]
        if file:
            files = [file]
        if components is not None:
            components = [i.to_all_dict() if isinstance(i, ActionRow) else i.to_dict() for i in components]

        allowed_mentions = _allowed_mentions(self._state, allowed_mentions)

        payload = self._get_payload(
            content=content,
            embed=embeds,
            allowed_mentions=allowed_mentions,
            components=components,
        )

        if files:
            form = _files_to_form(files=files, payload=payload)
        else:
            form = None

        if message_id == "@original":
            resp = await self.http.edit_initial_response(payload=payload, form=form, files=files, data=self.data)
        else:
            resp = await self.http.edit_followup(
                message_id=message_id,
                payload=payload,
                form=form,
                files=files,
                data=self.data
            )
        ret = Message(state=self._state, channel=self.channel, data=resp)
        if self.deferred:
            self.deferred = False

        if files:
            for file in files:
                file.close()
        return ret

    async def delete(self, message_id="@original"):
        if message_id == "@original":
            await self.http.delete_initial_response(data=self.data)
        else:
            await self.http.delete_followup(message_id=message_id, data=self.data)
        return


class ModalPossible:
    async def modal(
            self,
            custom_id: str,
            title: str,
            components: List[Components]
    ):
        self.responded = True
        payload = {
            "type": 9,
            "data": {
                "custom_id": custom_id,
                "title": title,
                "components": [i.to_all_dict() if isinstance(i, ActionRow) else i.to_dict() for i in components]
            }
        }
        return await self.http.post_initial_response(
            data=self.data,
            payload=payload
        )


class BaseApplicationContext(InteractionContext, ModalPossible):
    def __init__(self, payload: dict, client):
        super().__init__(payload, client)
        self._state: ConnectionState = getattr(client, "_connection")
        self._from_data(
            payload.get("data", {})
        )

    @classmethod
    def from_original_data(cls, response, client, _cls=None):
        new_cls: BaseApplicationContext = super().from_original_data(response, client, _cls=cls)
        new_cls._from_data(
            response.data
        )
        return new_cls

    def _from_data(self, data):
        self.target_id = data.get("target_id")
        self._resolved = data.get("resolved", {})

    def target(self, target_type, target_id: int = None):
        if target_id is None:
            target_id = self.target_id

        if target_type == "message" and "messages" in self._resolved:
            resolved = self._resolved.get("messages", {})
            data = Message(
                state=self._state,
                channel=self.channel,
                data=resolved.get(str(target_id))
            )
            return data
        elif target_type == "members" and "members" in self._resolved and self.guild_id is not None:
            resolved = self._resolved.get("members", {})
            member_data = resolved.get(
                str(target_id), {}
            )

            # USER DATA INJECT!
            user_resolved = self._resolved.get("users", {})
            user_data = user_resolved.get(
                str(target_id), {}
            )
            member_data['user'] = user_data

            data = discord.Member(data=member_data, state=self._state, guild=self.guild)
            return data
        elif target_type == "users" and "users" in self._resolved:
            resolved = self._resolved.get("users", {})
            data = discord.User(data=resolved.get(
                str(target_id), {}
            ), state=self._state)
            return data
        elif target_type == "roles" and "roles" in self._resolved and self.guild is not None:
            resolved = self._resolved.get("roles", {})
            data = discord.Role(data=resolved.get(
                str(target_id), {}
            ), state=self._state, guild=self.guild)
            return data
        elif target_type == "channels" and "channels" in self._resolved:
            resolved = self._resolved.get("channels", {})
            data = resolved.get(str(target_id))
            if data is None:
                return

            factory, ch_type = discord._channel_factory(data['type'])
            if factory is None:
                raise discord.InvalidData('Unknown channel type {type} for channel ID {id}.'.format_map(data))

            if ch_type in (discord.ChannelType.group, discord.ChannelType.private):
                channel = factory(me=self.client.user, data=data, state=self._state)
            else:
                if 'position' not in data:
                    data['position'] = None

                guild_id = int(data.get('guild_id') or self.guild_id)
                guild = self.client.get_guild(guild_id) or discord.Object(id=guild_id)
                channel = factory(guild=guild, state=self._state, data=data)

            return channel


class SubcommandContext(BaseApplicationContext):
    def __init__(self, original_payload: dict, payload: dict, client):
        super().__init__(original_payload, client)
        self.name = payload.get('name')
        self.options = {}

        for option in payload.get("options", []):
            key = option.get("name")
            value = option.get("value")
            option_type = option.get("type")

            if option_type == 1:
                self.options['subcommand'] = SubcommandContext(original_payload, option, client)
            elif option_type == 3:
                self.options[key]: str = value
            elif option_type == 4:
                self.options[key]: int = value
            elif option_type == 5:
                self.options[key] = bool(value)
            elif option_type == 6:
                if self.guild is not None:
                    self.options[key] = self.guild.get_member(value) or self.target('members', target_id=value)
                else:
                    self.options[key] = client.get_user(value) or self.target('users', target_id=value)
            elif option_type == 7:
                self.options[key]: Optional[Union[channel_types]] = (
                        client.get_channel(value) or self.target('channels', target_id=value)
                )
            elif option_type == 8:
                self.options[key]: Optional[discord.Role] = (
                        self.guild.get_role(value) or self.target('roles', target_id=value)
                )
            elif option_type == 10:
                self.options[key]: float = float(value)
            elif option_type == 11:
                state: ConnectionState = getattr(client, "_connection")
                self.options[key]: discord.Attachment = discord.Attachment(data=value, state=state)
            else:
                self.options[key] = value


class ApplicationContext(BaseApplicationContext):
    def __init__(self, payload: dict, client):
        super().__init__(payload, client)
        self.type = payload.get("type", 2)
        data = payload.get("data", {})

        self.function = None
        self.parents = None

        self.application_type = data.get("type")
        self.name = data.get("name")
        if self.application_type == 1:
            self.options = {}
            self.option_focused = []
            for option in data.get("options", []):
                key = option.get("name")
                value = option.get("value")
                option_type = option.get("type")
                focused = option.get("focused", False)
                if focused:
                    self.option_focused.append(key)

                if option_type == 1:
                    self.options['subcommand'] = SubcommandContext(payload, option, client)
                elif option_type == 2:
                    self.options['subcommand_group'] = SubcommandContext(payload, option, client)
                elif option_type == 3:
                    self.options[key]: str = value
                elif option_type == 4:
                    self.options[key]: int = value
                elif option_type == 5:
                    self.options[key] = bool(value)
                elif option_type == 6:
                    if self.guild is not None:
                        self.options[key] = self.guild.get_member(value) or self.target('members', target_id=value)
                    else:
                        self.options[key] = client.get_user(value) or self.target('users', target_id=value)
                elif option_type == 7:
                    self.options[key]: Optional[Union[channel_types]] = (
                            client.get_channel(value) or self.target('channels', target_id=value)
                    )
                elif option_type == 8:
                    self.options[key]: Optional[discord.Role] = (
                            self.guild.get_role(value) or self.target('roles', target_id=value)
                    )
                elif option_type == 10:
                    self.options[key]: float = float(value)
                elif option_type == 11:
                    state: ConnectionState = getattr(client, "_connection")
                    self.options[key]: discord.Attachment = discord.Attachment(data=value, state=state)
                else:
                    self.options[key] = value

        self.command_id = data.get("id")

    @property
    def content(self):
        if self.application_type == 1:
            options = [str(self.options[i]) for i in self.options.keys()]
            return f"/{self.name} {' '.join(options)}"
        else:
            return f"/{self.name}"

    @property
    def is_context(self) -> bool:
        return self.function is not None


class ComponentsContext(InteractionContext, ModalPossible):
    def __init__(self, payload: dict, client):
        super().__init__(payload, client)
        self.type = payload.get("type", 3)
        data = payload.get("data", {})

        self.custom_id = data.get("custom_id")
        self.component_type = data.get("component_type")
        if self.component_type == 3:
            self.values: List[str] = data.get("values")
        else:
            self.values: List[str] = []

        self.message = Message(state=self._state, channel=self.channel, data=payload.get("message", {}))

    async def defer_update(self, hidden: bool = False):
        base = {"type": 6}
        if hidden:
            base["data"] = {"flags": 64}

        await self.http.post_initial_response(payload=base, data=self.data)
        self.deferred = True
        return

    async def update(
            self,
            content=None,
            *,
            tts: bool = False,
            embed: discord.Embed = None,
            embeds: List[discord.Embed] = None,
            file: discord.File = None,
            files: List[discord.File] = None,
            allowed_mentions: discord.AllowedMentions = None,
            components: List[Union[ActionRow, Button, Selection]] = None
    ):
        if file is not None and files is not None:
            raise InvalidArgument()
        if embed is not None and embeds is not None:
            raise InvalidArgument()

        content = str(content) if content is not None else None
        if embed is not None:
            embeds = [embed]
        if embeds is not None:
            embeds = [embed.to_dict() for embed in embeds]
        if file:
            files = [file]
        if components is not None:
            components = [i.to_all_dict() if isinstance(i, ActionRow) else i.to_dict() for i in components]

        allowed_mentions = _allowed_mentions(self._state, allowed_mentions)
        payload = self._get_payload(
            content=content,
            embed=embeds,
            tts=tts,
            allowed_mentions=allowed_mentions,
            components=components,
        )

        if files:
            form = _files_to_form(files=files, payload=payload)
        else:
            form = None

        if not self.responded:
            if files:
                await self.defer_update()

            if self.deferred:
                await self.http.edit_message(
                    channel_id=self.channel.id, message_id=self.message.id,
                    payload=payload, form=form, files=files
                )
                self.deferred = False
            else:
                await self.http.post_initial_response(
                    payload={
                        "type": 7,
                        "data": payload
                    },
                    data=self.data
                )
            self.responded = True
        else:
            await self.http.post_followup(payload=payload, form=form, files=files, data=self.data)

        if files:
            for i in files:
                i.close()


class AutocompleteContext(ApplicationContext):
    def __init__(self, payload: dict, client):
        super().__init__(payload, client)
        self.type = payload.get("type", 4)

    async def autocomplete(self, choices: List[CommandOptionChoice]):
        self.responded = True
        payload = {
            "type": 8,
            "data": {
                "choices": [choice.to_dict() for choice in choices]
            }
        }
        return await self.http.post_initial_response(
            data=self.data,
            payload=payload
        )


class ModalContext(InteractionContext):
    def __init__(self, payload: dict, client):
        super().__init__(payload, client)
        self.type = payload.get("type", 5)
        data = payload.get("data", {})

        self.custom_id = data.get("custom_id")
        self.components = [
            from_payload(component) for component in data.get("", [])
        ]
