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


class SlashRoute(Route):
    BASE = "https://discord.com/api/v9"


class InteractionData:
    def __init__(self, interaction_token, interaction_id=None, application_id=None):
        self.id = str(interaction_id)
        self.application = str(application_id)
        self.token: str = interaction_token


class HttpClient:
    def __init__(self, http: discord.http.HTTPClient):
        self.http = http

    async def post_initial_response(self, data: InteractionData, payload: dict):
        r = SlashRoute(
            "POST", "/interactions/{id}/{token}/callback", id=data.id, token=data.token
        )
        return await self.http.request(r, json=payload)

    async def get_initial_response(self, data: InteractionData):
        r = SlashRoute(
            "GET", "/webhooks/{id}/{token}/messages/@original", id=data.application, token=data.token
        )
        return await self.http.request(r)

    async def edit_initial_response(self, data: InteractionData, payload: dict = None, form=None, files=None):
        if files is not None or form is not None:
            return await self.edit_followup(message_id="@original", form=form, files=files, data=data)
        return await self.edit_followup(message_id="@original", payload=payload, data=data)

    async def delete_initial_response(self, data: InteractionData):
        await self.delete_followup(message_id="@original", data=data)

    async def post_followup(self, data: InteractionData, payload: dict = None, form=None, files=None):
        r = SlashRoute(
            "POST", "/webhooks/{id}/{token}", id=data.application, token=data.token
        )
        if files is not None or form is not None:
            return await self.http.request(r, form=form, files=files)
        return await self.http.request(r, json=payload)

    async def edit_followup(self, data: InteractionData, message_id, payload: dict = None, form=None, files=None):
        r = SlashRoute(
            "PATCH", "/webhooks/{id}/{token}/messages/{message_id}",
            id=data.application, token=data.token, message_id=message_id
        )
        if files is not None or form is not None:
            return await self.http.request(r, form=form, files=files)
        return await self.http.request(r, json=payload)

    async def delete_followup(self, data: InteractionData, message_id):
        r = SlashRoute(
            "DELETE", "/webhooks/{id}/{token}/messages/{message_id}",
            id=data.application, token=data.token, message_id=message_id
        )
        await self.http.request(r)

    async def create_message(self, channel_id, payload: dict = None, form=None, files=None):
        r = SlashRoute(
            'POST', '/channels/{channel_id}/messages', channel_id=channel_id
        )
        if files is not None or form is not None:
            return await self.http.request(r, form=form, files=files)
        return await self.http.request(r, json=payload)

    async def edit_message(self, channel_id, message_id, payload: dict = None, form=None, files=None):
        r = SlashRoute(
            'PATCH', '/channels/{channel_id}/messages/{message_id}', channel_id=channel_id, message_id=message_id
        )
        if files is not None or form is not None:
            return await self.http.request(r, form=form, files=files)
        return await self.http.request(r, json=payload)

    async def register_command(self, application_id: int, payload: dict = None):
        r = SlashRoute(
            'POST', '/applications/{application_id}/commands', application_id=application_id
        )
        return await self.http.request(r, json=payload)

    async def get_commands(self, application_id: int):
        r = SlashRoute(
            'GET', '/applications/{application_id}/commands', application_id=application_id
        )
        return await self.http.request(r)

    async def get_command(self, application_id: int, command_id: int):
        r = SlashRoute(
            'GET', '/applications/{application_id}/commands/{command_id}',
            application_id=application_id, command_id=command_id
        )
        return await self.http.request(r)

    async def edit_command(self, application_id: int, command_id: int, payload: dict = None):
        r = SlashRoute(
            'PATCH', '/applications/{application_id}/commands/{command_id}',
            application_id=application_id, command_id=command_id
        )
        return await self.http.request(r, json=payload)

    async def delete_command(self, application_id: int, command_id: int, payload: dict = None):
        r = SlashRoute(
            'DELETE', '/applications/{application_id}/commands/{command_id}',
            application_id=application_id, command_id=command_id
        )
        return await self.http.request(r, json=payload)
