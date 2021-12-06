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

import inspect
import logging
import os
import zlib

import discord
from discord.ext import commands
from typing import Optional, Dict, Union

from .commands import ApplicationCommand, BaseCommand, from_payload, command_types
from .components import DetectComponent
from .listener import Listener
from .http import HttpClient

log = logging.getLogger()


class ClientBase(commands.bot.BotBase):
    def __init__(
            self,
            command_prefix,
            global_sync_command: bool = False,
            **options
    ):
        if discord.version_info.major >= 2:
            options['enable_debug_events'] = True
        super().__init__(command_prefix, **options)
        self.global_sync_command = global_sync_command
        self.interaction_http = HttpClient(self.http)

        self._buffer = bytearray()
        self._zlib = zlib.decompressobj()

        self._application_id_value = None
        self._interactions_of_group = []
        self._interactions: Dict[str, command_types] = dict()
        self._fetch_interactions: Optional[Dict[str, ApplicationCommand]] = None

        self._detect_components: Dict[str, DetectComponent] = dict()

        self.__sync_command_before_ready_register = []
        self.__sync_command_before_ready_popping = []

        self.add_listener(self._sync_command_task, "on_ready")

    async def register_command(self, command: ApplicationCommand):
        command_ids = await self._fetch_command_cached()
        if command.name in command_ids:
            raise commands.CommandRegistrationError(command.name)
        return await self.interaction_http.register_command(
            await self._application_id(),
            payload=command.to_register_dict()
        )

    async def edit_command(self, command: ApplicationCommand, command_id: int = None):
        if command_id is None and command.id is None:
            command_ids = await self._fetch_command_cached()
            if command.name not in command_ids:
                raise commands.CommandNotFound(f'Command "{command.name}" is not found')

            command_id = command_ids[command.name].id
        return await self.interaction_http.edit_command(
            await self._application_id(),
            command_id=command_id or command.id,
            payload=command.to_register_dict()
        )

    async def delete_command(self, command: ApplicationCommand, command_id: int = None):
        if command_id is None and command.id is None:
            command_ids = await self._fetch_command_cached()
            if command.name not in command_ids:
                raise commands.CommandNotFound(f'Command "{command.name}" is not found')

            command_id = command_ids[command.name].id
        return await self.interaction_http.delete_command(
            await self._application_id(),
            command_id=command_id or command.id,
            payload=command.to_register_dict()
        )

    async def _application_id(self):
        if self._application_id_value is None:
            application_info: discord.AppInfo = await self.application_info()
            self._application_id_value = application_info.id
        return self._application_id_value

    async def fetch_commands(self) -> Dict[str, command_types]:
        data = await self.interaction_http.get_commands(
            await self._application_id()
        )
        if isinstance(data, list):
            result = {}
            for x in data:
                _x = from_payload(x)
                result[_x.name] = _x
            self._fetch_interactions = result
        else:
            _result = from_payload(data)
            result = {_result.name: _result}
        return result

    async def _fetch_command_cached(self) -> Dict[str, ApplicationCommand]:
        if self._fetch_interactions is None:
            await self.fetch_commands()
        return self._fetch_interactions

    async def _sync_command(self, command: command_types):
        await self.wait_until_ready()
        fetch_data = await self._fetch_command_cached()
        if command.name in fetch_data.keys():
            command_id = fetch_data[command.name].id
            if command.name in self._interactions:
                self._interactions[command.name].id = command_id
            if fetch_data[command.name] != command:
                await self.edit_command(command=command)
        else:
            await self.register_command(command)
        return

    async def _sync_command_popping(self, command: command_types):
        await self.wait_until_ready()
        fetch_data = await self._fetch_command_cached()
        if command.name in fetch_data.keys():
            command_id = fetch_data[command.name].id
            await self.delete_command(command, command_id=command_id)
        return

    def load_extensions(self, package: str, directory: str = None) -> None:
        if directory is not None:
            package = os.path.join(directory, package)
        cogs = [
            "{0}.{1}".format(package, file[:-3])
            for file in os.listdir(package)
            if file.endswith(".py")
        ]
        for cog in cogs:
            self.load_extension(cog)
        return

    async def _sync_command_task(self):
        if len(self.__sync_command_before_ready_register) != 0:
            log.debug(
                f"Register registered commands before bot is ready. List: "
                f"{', '.join([x.name for x in self.__sync_command_before_ready_register])}"
            )
        while len(self.__sync_command_before_ready_register) != 0:
            command = self.__sync_command_before_ready_register.pop()
            await self._sync_command(command=command)
        while len(self.__sync_command_before_ready_popping) != 0:
            command = self.__sync_command_before_ready_popping.pop()
            await self._sync_command_popping(command=command)

        if self.global_sync_command:
            log.info("global_sync_command is activated. Delete unregistered commands on client.")
            popping_data = await self._fetch_command_cached()
            for already_cmd in self._interactions.keys():
                if already_cmd in popping_data:
                    del popping_data[already_cmd]

            for cmd in popping_data.values():
                await self.delete_command(cmd)

    def add_interaction(
            self,
            command: command_types,
            sync_command: bool = None,
            _parent=None
    ):
        if sync_command is None:
            sync_command = self.global_sync_command

        if command.name in self._interactions:
            raise commands.CommandRegistrationError(command.name)

        if _parent is not None:
            command.parents = _parent
        self._interactions[command.name] = command

        if sync_command:
            if self.is_ready():
                self._schedule_event(self._sync_command, "sync_command", command=command)
            else:
                self.__sync_command_before_ready_register.append(command)
        return

    def get_interaction(self):
        return self._interactions.values()

    def delete_interaction(
            self,
            command: command_types,
            sync_command: bool = None
    ):
        if sync_command is None:
            sync_command = self.global_sync_command

        if command.name not in self._interactions:
            raise commands.CommandNotFound(f'Command "{command.name}" is not found')

        self._interactions.pop(command.name)

        if sync_command:
            if self.is_ready():
                self._schedule_event(self._sync_command_popping, "sync_command", command=command)
            else:
                self.__sync_command_before_ready_popping.append(command)

    def add_icog(
            self,
            icog: type
    ):
        self._interactions_of_group.append(icog)
        for func, attr in inspect.getmembers(icog):
            if isinstance(attr, BaseCommand):
                attr.parents = icog
                self.add_interaction(attr, attr.sync_command)
            elif isinstance(attr, Listener):
                self.add_listener(attr.callback, name=attr.name)
            elif isinstance(attr, DetectComponent):
                attr.parents = icog
                pass
        return


class Client(ClientBase, discord.Client):
    pass


class AutoShardedClient(ClientBase, discord.AutoShardedClient):
    pass
