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
import inspect
import logging
import os
import zlib
from typing import Optional, Dict, List

import discord
from discord.ext import commands
from discord.gateway import DiscordWebSocket
from discord.state import ConnectionState

from .commands import (
    ApplicationCommand, BaseCommand, SubCommand, SubCommandGroup,
    from_payload, command_types, decorator_command_types, get_signature_option
)
from .components import DetectComponent
from .http import HttpClient
from .interaction import ApplicationContext, ComponentsContext, AutocompleteContext
from .listener import Listener
from .message import Message
from .utils import _from_json

log = logging.getLogger()


class ClientBase(commands.bot.BotBase):
    def __init__(
            self,
            command_prefix=None,
            global_sync_command: bool = False,
            **options
    ):
        if discord.version_info.major >= 2:
            options['enable_debug_events'] = True
        super().__init__(command_prefix, **options)
        self.global_sync_command = global_sync_command
        self.interaction_http = HttpClient(self.http)

        self.__buffer = bytearray()
        self.__zlib = zlib.decompressobj()

        self._application_id_value = None
        self._interactions_of_group = []
        self._interactions: List[Dict[str, decorator_command_types]] = [dict(), dict(), dict()]
        self._fetch_interactions: Optional[
            Dict[
                str, ApplicationCommand
            ]
        ] = None

        self._detect_components: Dict[
            str,
            List[DetectComponent]
        ] = dict()

        self.__sync_command_before_ready_register = []
        self.__sync_command_before_ready_popping = []

        self._deferred_components: Dict[str, list] = dict()

        self.add_listener(self._sync_command_task, "on_ready")

    async def process_commands(self, message):
        if self.command_prefix is not None:
            return await super().process_commands(message)
        return

    async def get_prefix(self, message):
        if self.command_prefix is not None:
            return await super().get_prefix(message)
        return

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
            if command.name in self._interactions[command.type.value - 1]:
                self._interactions[command.type.value - 1][command.name].id = command_id
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
            _package = os.path.join(directory, package)
        else:
            _package = package
        cogs = [
            "{0}.{1}".format(package, file[:-3])
            for file in os.listdir(_package)
            if file.endswith(".py")
        ]
        for cog in cogs:
            self.load_extension(cog)
        return

    async def _sync_command_task(self):
        if len(self.__sync_command_before_ready_register) != 0:
            log.info(
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
            for interaction in self._interactions:
                for already_cmd in interaction:
                    if already_cmd in popping_data:
                        del popping_data[already_cmd]

            for cmd in popping_data.values():
                await self.delete_command(cmd)

    def add_detect_component(
            self,
            detect_component: DetectComponent
    ):
        name = detect_component.custom_id
        if name in self._detect_components:
            self._detect_components[name].append(detect_component)
        else:
            self._detect_components[name] = [detect_component]
        return

    def get_detect_component(self):
        return self._detect_components

    def delete_detect_component(
            self,
            custom_id: str,
            detect_component: DetectComponent = None
    ):
        if detect_component is None:
            self._detect_components.pop(custom_id)
        else:
            for i, x in enumerate(self._detect_components[custom_id]):
                if x == detect_component:
                    self._detect_components[custom_id].pop(i)
                    break
        return

    def add_interaction(
            self,
            command: decorator_command_types,
            sync_command: bool = None,
            _parent=None
    ):
        if sync_command is None:
            sync_command = self.global_sync_command

        if command.name in self._interactions[command.type.value - 1]:
            raise commands.CommandRegistrationError(command.name)

        if _parent is not None:
            command.cog = _parent
            if not command.is_subcommand:
                command.options = get_signature_option(command.func, command.base_options, skipping_argument=2)
        else:
            if not command.is_subcommand:
                command.options = get_signature_option(command.func, command.base_options, skipping_argument=1)
        self._interactions[command.type.value - 1][command.name] = command

        if sync_command:
            if self.is_ready():
                self._schedule_event(self._sync_command, "sync_command", command=command)
            else:
                self.__sync_command_before_ready_register.append(command)
        return

    def get_interaction(self):
        result = []
        for x in self._interactions:
            result += x.values()
        return result

    def delete_interaction(
            self,
            command: command_types,
            sync_command: bool = None
    ):
        if sync_command is None:
            sync_command = self.global_sync_command

        if command.name not in self._interactions[command.type.value - 1]:
            raise commands.CommandNotFound(f'Command "{command.name}" is not found')

        self._interactions[command.type.value - 1].pop(command.name)

        if sync_command:
            if self.is_ready():
                self._schedule_event(self._sync_command_popping, "sync_command", command=command)
            else:
                self.__sync_command_before_ready_popping.append(command)

    def add_icog(
            self,
            icog
    ):
        self._interactions_of_group.append(icog)
        for func, attr in inspect.getmembers(icog):
            if isinstance(attr, BaseCommand):
                attr: decorator_command_types
                self.add_interaction(attr, attr.sync_command, icog)
            elif isinstance(attr, Listener):
                attr.parents = icog
                self.add_listener(attr.__call__, name=attr.name)
            elif isinstance(attr, DetectComponent):
                attr.parents = icog
                self.add_detect_component(attr)
            elif inspect.iscoroutinefunction(attr):
                if hasattr(attr, '__cog_listener__') and hasattr(attr, '__cog_listener_names__'):
                    if not attr.__cog_listener__:
                        continue
                    for name in attr.__cog_listener_names__:
                        self.add_listener(attr, name=name)
        return

    async def on_socket_raw_receive(self, msg):
        if type(msg) is bytes:
            self.__buffer.extend(msg)

            if len(msg) < 4 or msg[-4:] != b'\x00\x00\xff\xff':
                return
            try:
                msg = self.__zlib.decompress(self.__buffer)
            except zlib.error as error:
                # zlib.error: Error -3 while decompressing data: invalid stored block lengths
                log.debug("zlib.error: {0}\npayload data: {1}".format([str(arg) for arg in error.args], msg))
                log.warning('zlib.error: Client will reset zlib decompress object')
                self.__zlib = zlib.decompressobj()
                msg = self.__zlib.decompress(self.__buffer)
            msg = msg.decode('utf-8')
            self.__buffer = bytearray()
        payload = _from_json(msg)

        data = payload.get("d", {})
        t = payload.get("t", "")
        op = payload.get("op", "")

        if op != DiscordWebSocket.DISPATCH:
            return
        self.dispatch("payload_receive", payload=payload)

        state: ConnectionState = self._connection
        if t == "INTERACTION_CREATE":
            state.dispatch('interaction_raw_create', payload)
            if data.get("type") == 2:
                result = ApplicationContext(data, self)
                if len(self._interactions[result.application_type - 1]) != 0:
                    state.dispatch('interaction_command', result)
            elif data.get("type") == 3:
                result = ComponentsContext(data, self)
                await self.process_components(result)
                state.dispatch('components', result)
            elif data.get("type") == 4:
                result = AutocompleteContext(data, self)
                state.dispatch('autocomplete', result)
            return
        elif t == "MESSAGE_CREATE":
            channel, _ = getattr(state, "_get_guild_channel")(data)
            message = Message(state=state, data=data, channel=channel)
            state.dispatch('interaction_message', message)
            # @deprecated
            # if len(self._interactions) != 0:
            #     command = MessageCommand(state=state, data=data, channel=channel)
            #     state.dispatch('interaction_command', command)
            return

    async def process_interaction(self, ctx: ApplicationContext):
        _state: ConnectionState = self._connection
        command = self._interactions[ctx.application_type - 1].get(ctx.name)
        if command is None:
            return

        _state.dispatch("command", ctx)

        try:
            func = ctx.function = command
            if command.cog is not None:
                ctx.parents = command.cog
            if await self.can_run(ctx, call_once=True):
                _option = ctx.options
                if command.is_subcommand:
                    options = command.options
                    if 'subcommand_group' in ctx.options:
                        sub_command_group = ctx.options['subcommand_group']
                        for opt in command.options:
                            if isinstance(opt, SubCommandGroup) and sub_command_group.name == opt.name:
                                options = opt.options
                                break
                    sub_command = ctx.options['subcommand']
                    for opt in options:
                        if opt.name == sub_command.name and isinstance(opt, SubCommand):
                            ctx.function = func = opt
                            ctx.parents = None
                            if opt.cog is not None:
                                ctx.parents = opt.cog
                            _option = sub_command.options
                            break
                if await func.can_run(ctx):
                    await func.callback(ctx, **_option)
            else:
                raise commands.errors.CheckFailure('The global check once functions failed.')
        except Exception as error:
            if isinstance(error, commands.errors.CheckFailure):
                _state.dispatch("command_permission_error", ctx, error)
            _state.dispatch("interaction_command_error", ctx, error)
            raise error
        else:
            _state.dispatch("command_complete", ctx)
        return

    async def on_interaction_command(self, ctx: ApplicationContext):
        await self.process_interaction(ctx)
        return

    def wait_for_component(self, custom_id: str, check=None, timeout=None):
        future = self.loop.create_future()
        if check is None:
            def _check(_: ComponentsContext):
                return True
            check = _check

        ev = custom_id.lower()
        try:
            listeners = self._deferred_components[ev]
        except KeyError:
            listeners = []
            self._deferred_components[ev] = listeners

        listeners.append((future, check))
        return asyncio.wait_for(future, timeout)

    async def process_components(self, component: ComponentsContext):
        _state: ConnectionState = self._connection

        detect_component = self._detect_components.get(component.custom_id)
        if detect_component is None:
            detect_component = []
        active_component = []
        for _component in detect_component:
            if _component.type_id == component.component_type or _component.type is None:

                try:
                    if await self.can_run(component, call_once=True):
                        if await _component.can_run(component):
                            await _component.callback(component)
                    else:
                        raise commands.errors.CheckFailure('The global check once functions failed.')
                except Exception as error:
                    if isinstance(error, commands.errors.CheckFailure):
                        _state.dispatch("component_permission_error", component, error)
                    _state.dispatch("component_error", component, error)
                else:
                    _state.dispatch("component_complete", component)
                    active_component.append(component)

        listeners = self._deferred_components.get(component.custom_id)
        detect_component_wait_for = []
        if listeners is not None:
            removed = []
            for index, (future, check) in enumerate(listeners):
                if future.cancelled():
                    removed.append(index)
                    continue

                try:
                    result = check(component)
                except Exception as exc:
                    future.set_exception(exc)
                    removed.append(index)
                else:
                    if result:
                        detect_component_wait_for.append(component)
                        future.set_result(component)
                        removed.append(index)

            if len(removed) == len(listeners):
                self._deferred_components.pop(component.custom_id)
            else:
                for idx in reversed(removed):
                    listeners.pop(idx)

        if len(detect_component_wait_for) == 0 and len(active_component) == 0:
            _state.dispatch("components_cancelled", component)
        return


class Client(ClientBase, discord.Client):
    pass


class AutoShardedClient(ClientBase, discord.AutoShardedClient):
    pass
