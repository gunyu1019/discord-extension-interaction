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

from typing import NamedTuple, TYPE_CHECKING

from discord.http import Route

if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Any, Dict, Optional, Union

    from discord.file import File
    from discord.http import HTTPClient


class InteractionData(NamedTuple):
    """The minimal identity of an interaction required to respond over the REST API.

    Attributes
    ----------
    id: int
        The interaction's ID. Used for the initial ``callback`` response.
    application_id: int
        The application's ID. Used as the webhook id for the original response and followups.
    token: str
        The interaction's continuation token.
    """

    id: int
    application_id: int
    token: str


class InteractionHTTPClient:
    """A thin wrapper around :class:`discord.http.HTTPClient` for interaction responses.

    Every route used here is a permanent Discord REST endpoint
    (``/interactions/{id}/{token}/callback`` and the interaction followup webhooks),
    so this stays stable across discord.py releases while delegating rate-limit
    handling, retries and error translation to the underlying ``HTTPClient``.

    ``webhook_id`` / ``webhook_token`` are used as the route parameter names so that
    :attr:`discord.http.Route.major_parameters` buckets these requests the same way
    discord.py buckets its own interaction and webhook calls.
    """

    def __init__(self, http: HTTPClient):
        self.http = http

    # -- Initial response -------------------------------------------------
    async def post_initial_response(
        self, data: InteractionData, payload: Dict[str, Any]
    ):
        route = Route(
            "POST",
            "/interactions/{webhook_id}/{webhook_token}/callback",
            webhook_id=data.id,
            webhook_token=data.token,
        )
        return await self.http.request(route, json=payload)

    async def get_initial_response(self, data: InteractionData):
        route = Route(
            "GET",
            "/webhooks/{webhook_id}/{webhook_token}/messages/@original",
            webhook_id=data.application_id,
            webhook_token=data.token,
        )
        return await self.http.request(route)

    async def edit_initial_response(
        self,
        data: InteractionData,
        payload: Optional[Dict[str, Any]] = None,
        form: Optional[list[Dict[str, Any]]] = None,
        files: Optional[Sequence[File]] = None,
    ):
        # ``@original`` is baked into the path (not passed as a parameter) so that
        # ``Route`` does not percent-encode the ``@`` into ``%40``.
        route = Route(
            "PATCH",
            "/webhooks/{webhook_id}/{webhook_token}/messages/@original",
            webhook_id=data.application_id,
            webhook_token=data.token,
        )
        if form:
            return await self.http.request(route, form=form, files=files)
        return await self.http.request(route, json=payload)

    async def delete_initial_response(self, data: InteractionData):
        route = Route(
            "DELETE",
            "/webhooks/{webhook_id}/{webhook_token}/messages/@original",
            webhook_id=data.application_id,
            webhook_token=data.token,
        )
        return await self.http.request(route)

    # -- Followup -------------------------------------------------------
    async def post_followup(
        self,
        data: InteractionData,
        payload: Optional[Dict[str, Any]] = None,
        form: Optional[list[Dict[str, Any]]] = None,
        files: Optional[Sequence[File]] = None,
    ):
        route = Route(
            "POST",
            "/webhooks/{webhook_id}/{webhook_token}",
            webhook_id=data.application_id,
            webhook_token=data.token,
        )
        if form:
            return await self.http.request(route, form=form, files=files)
        return await self.http.request(route, json=payload)

    async def edit_followup(
        self,
        data: InteractionData,
        message_id: Union[int, str],
        payload: Optional[Dict[str, Any]] = None,
        form: Optional[list[Dict[str, Any]]] = None,
        files: Optional[Sequence[File]] = None,
    ):
        route = Route(
            "PATCH",
            "/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}",
            webhook_id=data.application_id,
            webhook_token=data.token,
            message_id=message_id,
        )
        if form:
            return await self.http.request(route, form=form, files=files)
        return await self.http.request(route, json=payload)

    async def delete_followup(
        self, data: InteractionData, message_id: Union[int, str]
    ):
        route = Route(
            "DELETE",
            "/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}",
            webhook_id=data.application_id,
            webhook_token=data.token,
            message_id=message_id,
        )
        return await self.http.request(route)
