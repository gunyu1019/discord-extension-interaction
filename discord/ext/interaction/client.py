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

import os
import discord
import zlib
from discord.ext import commands
from discord.gateway import DiscordWebSocket
from discord.state import ConnectionState

from .commands import Command
from .utils import _from_json


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
        self.all_interactions = {}

        self._buffer = bytearray()
        self._zlib = zlib.decompressobj()

    async def register_command(self, command: Command):
        data = {
            "name": command.name
        }

        if command.description is not None:
            data["description"] = command.description
        if command.options is not None:
            data["options"] = [
                option.to_dict() for option in command.options
            ]
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

    def add_interaction(
            self,
            command: Command,
            sync_command: bool = None,
            _parent=None
    ):
        if sync_command is None:
            sync_command = self.global_sync_command

        if command.name in self.all_interactions:
            raise commands.CommandRegistrationError(command.name)

        if _parent is not None:
            command.parents = _parent
        self.all_interactions[command.name] = command
        if len(command.aliases) != 0:
            for alias in command.aliases:
                if alias in self.all_interactions:
                    continue
                self.all_interactions[alias] = command
        return

    def add_icog(
            self,
            _class
    ):
        return

    async def on_socket_raw_receive(self, msg):
        if type(msg) is bytes:
            self._buffer.extend(msg)

            if len(msg) < 4 or msg[-4:] != b'\x00\x00\xff\xff':
                return

            msg = self._zlib.decompress(self._buffer)
            msg = msg.decode('utf-8')
            self._buffer = bytearray()
        payload = _from_json(msg)

        data = payload.get("d", {})
        t = payload.get("t", "")
        op = payload.get("op", "")

        if op != DiscordWebSocket.DISPATCH:
            return

        state: ConnectionState = self._connection

    async def on_ready(self):
        return


class Client(ClientBase, discord.Client):
    pass


class AutoShardedClient(ClientBase, discord.AutoShardedClient):
    pass
