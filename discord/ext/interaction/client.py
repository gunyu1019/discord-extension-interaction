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
import copy
import importlib
import importlib.machinery
import importlib.util
import inspect
import logging
import os
import sys
import types
from typing import TYPE_CHECKING

import discord.http
from discord.state import ConnectionState

from discord.ext.interaction.commands import (
    ApplicationCommand,
    from_payload,
    command_types,
)
from discord.ext.interaction.sync import (
    same_command_declaration,
    CommandRegistry,
    SyncPolicyStore,
    plan_sync,
    SyncPlan,
    apply_sync_plan,
    SyncResult,
)
from discord.ext.interaction.interaction_dispatcher import (
    InteractionDispatcher,
)
from discord.ext.interaction.activity_binding import ActivityBinding
from discord.ext.interaction.models.activity_command import ActivityCommand
from discord.ext.interaction.models.command_scope import GlobalScope, GuildScope
from discord.ext.interaction.models.sync_command import SyncCommand
from discord.ext.interaction.components import DetectComponent
from discord.ext.interaction.core import (
    SubCommand,
    SubCommandGroup,
    BaseCommand,
    decorator_command_types,
)
from discord.ext.interaction.enums import ApplicationCommandType
from discord.ext.interaction.errors import *
from discord.ext.interaction.interaction import (
    ApplicationContext,
    ComponentsContext,
    AutocompleteContext,
    ModalSubmitContext,
)
from discord.ext.interaction.message import Message
from discord.ext.interaction.command_api import (
    get_global_commands_with_localizations,
    get_guild_commands_with_localizations,
    create_guild_command,
    edit_guild_command,
    delete_guild_command,
    get_guild_command,
)
from discord.ext.interaction.command_sync_api import CommandSyncAPI
from discord.ext.interaction.utils import async_all

if TYPE_CHECKING:
    from discord.client import _ClientOptions  # noqa
    from typing import Any, Unpack

    from discord.ext.interaction._types import (
        CoroutineFunction,
        UserCheck,
        _Coroutine,
        T,
    )

log = logging.getLogger(__name__)


class ClientBase:
    # Mix-in for :class:`discord.Client` / :class:`discord.AutoShardedClient`.
    # Instantiated only through :class:`Client` / :class:`AutoShardedClient` below,
    # so ``super().__init__`` cooperatively reaches the real client constructor.
    _connection: discord.state.ConnectionState
    loop: asyncio.AbstractEventLoop
    http: discord.http.HTTPClient

    def __init__(
        self,
        global_sync_command: bool = False,
        intents: discord.Intents = discord.Intents.default(),
        **options: Unpack[_ClientOptions],
    ):
        super().__init__(intents=intents, **options)

        self.global_sync_command = global_sync_command

        self._pre_cached_application_id = None

        # Command of Group feature
        self._interactions_of_group = []
        self._command_registry = CommandRegistry()
        self._remote_command_registry = CommandRegistry()
        self._sync_policies = SyncPolicyStore()
        self._completed_sync_scopes: set[GlobalScope | GuildScope] = set()
        self._sync_policy_lock = asyncio.Lock()
        self._interactions: dict[
            ApplicationCommandType, dict[str, decorator_command_types]
        ] = {
            ApplicationCommandType.CHAT_INPUT: dict(),
            ApplicationCommandType.USER: dict(),
            ApplicationCommandType.MESSAGE: dict(),
            ApplicationCommandType.PRIMARY_ENTRY_POINT: dict(),
        }
        self._fetch_interactions: (
            dict[ApplicationCommandType, dict[str, command_types]] | None
        ) = None

        self._detect_components: dict[str, list[DetectComponent]] = dict()

        self.__sync_command_before_ready_register = []
        self.__sync_command_before_ready_popping = []

        self._checks: list[UserCheck] = []

        self._deferred_components: dict[str, list] = dict()
        self._deferred_global_components: list = list()

        self._multiple_setup_hook: list[CoroutineFunction] = list()

        self.extra_events: dict[str, list[CoroutineFunction]] = dict()
        self.__extensions: dict[str, types.ModuleType] = dict()

        self.extra_events["on_ready"] = [self.on_ready]

        self._install_interaction_parsers()

    def dispatch(self, event_name: str, /, *args: Any, **kwargs: Any) -> None:
        # super() will resolve to Client
        super().dispatch(event_name, *args, **kwargs)  # type: ignore
        ev = "on_" + event_name
        for event in self.extra_events.get(ev, []):
            self._schedule_event(event, ev, *args, **kwargs)  # type: ignore

    async def on_ready(self):
        await self._sync_command_task()

    async def setup_hook(self):
        await super(ClientBase, self).setup_hook()
        for func in self._multiple_setup_hook:
            await func()
        return

    # Command
    async def register_command(self, command: ApplicationCommand):
        """
        Register application commands with Discord Bot.

        Parameters
        ----------
        command: ApplicationCommand
            Application Command to register with discord bot.
        """
        if isinstance(command.scope, GuildScope):
            await self.fetch_guild_commands(command.scope.guild_id)
            existing = self._remote_command_registry.get(
                command.scope,
                command.type,
                command.name,
            )
            if existing is not None:
                raise CommandRegistrationError(command.name)
            return await create_guild_command(
                self.http,
                await self._application_id(),
                command.scope.guild_id,
                command.to_register_dict(),
            )
        command_ids = await self._fetch_command_cached()
        if command.name in command_ids[command.type]:
            raise CommandRegistrationError(command.name)
        return await self.http.upsert_global_command(
            await self._application_id(), payload=command.to_register_dict()
        )

    async def _find_command(
        self, command: ApplicationCommand, command_id: int
    ) -> int | None:
        if command_id is None and not command.id:
            if isinstance(command.scope, GuildScope):
                await self.fetch_guild_commands(command.scope.guild_id)
                found = self._remote_command_registry.get(
                    command.scope,
                    command.type,
                    command.name,
                )
            else:
                command_ids = await self._fetch_command_cached()
                found = command_ids[command.type].get(command.name)
            if found is None:
                raise CommandNotFound(f'Command "{command.name}" is not found')
            command_id = found.id
        return command_id

    async def edit_command(
        self, command: ApplicationCommand, command_id: int | None = None
    ):
        """Edit application commands with Discord Bot.

        Parameters
        ----------
        command : ApplicationCommand
            Application Command to edit with discord bot.
        command_id : Optional[int]
            Edit application command's id
        """
        command_id = await self._find_command(command, command_id)
        if isinstance(command.scope, GuildScope):
            return await edit_guild_command(
                self.http,
                await self._application_id(),
                command.scope.guild_id,
                int(command_id or command.id),
                command.to_register_dict(),
            )
        return await self.http.edit_global_command(
            await self._application_id(),
            command_id=command_id or command.id,
            payload=command.to_register_dict(),
        )

    async def delete_command(self, command: ApplicationCommand, command_id: int = None):
        """Delete application commands with Discord Bot.

        Parameters
        ----------
        command : ApplicationCommand
            Application Command to delete with discord bot.
        command_id : Optional[int]
            Delete application command's id
        """
        command_id = await self._find_command(command, command_id)
        if isinstance(command.scope, GuildScope):
            return await delete_guild_command(
                self.http,
                await self._application_id(),
                command.scope.guild_id,
                int(command_id or command.id),
            )
        return await self.http.delete_global_command(
            await self._application_id(), command_id=command_id or command.id
        )

    # Listener
    def add_listener(self, func: CoroutineFunction, name: str = None):
        """Add a listener for discord bot event call.

        Parameters
        ----------
        func
            Coroutine function to call when an event is called in Discord Bot
        name
        """
        name = name or func.__name__

        if not asyncio.iscoroutinefunction(func):
            raise TypeError("Listeners must be coroutines")

        if name in self.extra_events:
            self.extra_events[name].append(func)
        else:
            self.extra_events[name] = [func]

    def remove_listener(self, func: CoroutineFunction, name: str = None):
        """Delete a listener for discord bot event call.

        Parameters
        ----------
        func
            Coroutine function to delete from bot listeners
        name : Optional[str]
            Name of the listener for the invoked event.
        """
        if name in self.extra_events:
            try:
                self.extra_events[name].remove(func)
            except ValueError:
                pass

    def listen(self, name: str = None):
        """A decorator that add a listener to discord bot.

        Parameters
        ----------
        name : Optional[str]
            Name of the listener for the invoked event.
        """

        def decorator(func: CoroutineFunction) -> CoroutineFunction:
            self.add_listener(func, name)
            return func

        return decorator

    # Multiple setup_hook
    def add_setup_hook(self, func: CoroutineFunction):
        """Add a setup_hook

        Unlike the setup_hook in class:discord.Client,
        when discord bot ready to setup, it calls all the registered corutine functions at the same time.

        Parameters
        ----------
        func
            Coroutine function to call when setting up the loop
        """
        self._multiple_setup_hook.append(func)
        return

    def remove_setup_hook(self, func: CoroutineFunction):
        """Delete a setup_hook function from multi_setup_hook.

        Parameters
        ----------
        func
            Coroutine function to call when setting up the loop
        """
        try:
            self._multiple_setup_hook.remove(func)
        except ValueError:
            pass
        return

    def multiple_setup_hook(self):
        """A decorator that add a setup_hook to discord bot."""

        def decorator(func: CoroutineFunction) -> CoroutineFunction:
            self.add_setup_hook(func)
            return func

        return decorator

    # Application ID (from store data)
    async def _application_id(self):
        # ``Client.application_id`` is populated once the gateway READY arrives;
        # fall back to a REST lookup for calls made before then.
        if self.application_id is not None:
            return self.application_id
        if self._pre_cached_application_id is None:
            application_info: discord.AppInfo = await self.application_info()
            self._pre_cached_application_id = application_info.id
        return self._pre_cached_application_id

    @staticmethod
    def _empty_command_map() -> dict[ApplicationCommandType, dict[str, command_types]]:
        return {
            ApplicationCommandType.CHAT_INPUT: {},
            ApplicationCommandType.USER: {},
            ApplicationCommandType.MESSAGE: {},
            ApplicationCommandType.PRIMARY_ENTRY_POINT: {},
        }

    async def fetch_commands(
        self,
    ) -> dict[ApplicationCommandType, dict[str, command_types]]:
        """Fetch and update all application commands registered in discord to discord bot."""
        data = await get_global_commands_with_localizations(
            self.http, await self._application_id()
        )
        result = self._empty_command_map()
        parsed = []
        for x in data:
            _x = from_payload(x)
            result[ApplicationCommandType(_x.type)][_x.name] = _x
            parsed.append(_x)
        self._remote_command_registry.replace_scope(GlobalScope(), parsed)
        self._fetch_interactions = result
        return result

    async def fetch_guild_commands(self, guild_id: int):
        """Fetch a guild's commands using complete localization dictionaries."""
        scope = GuildScope(guild_id)
        data = await get_guild_commands_with_localizations(
            self.http,
            await self._application_id(),
            guild_id,
        )
        parsed = [from_payload({**item, "guild_id": str(guild_id)}) for item in data]
        self._remote_command_registry.replace_scope(scope, parsed)
        return self._remote_command_registry.for_scope(scope)

    async def fetch_command(
        self,
        command_id: int,
        use_cached: bool = False,
        command_type: ApplicationCommandType = None,
        scope: GlobalScope | GuildScope | None = None,
    ) -> command_types:
        """Fetches and updates the application commands specified in the discord to the client.

        Parameters
        ----------
        command_id : int
            ID of application command to load
        use_cached : Optional[bool]
            Look for it in preloaded application command list.
            If application command list is not found in preloaded list, it is automatically updated.
        command_type : Optional[ApplicationCommandType]
            Application Command Type. Default value is ``CHAT_INPUT``

        Returns
        -------
            Retrieves application command data registered in discord.
        """
        if command_type is None:
            command_type = ApplicationCommandType.CHAT_INPUT

        if isinstance(scope, GuildScope):
            if use_cached:
                for candidate in self._remote_command_registry.for_scope(
                    scope
                ).values():
                    if str(candidate.id) == str(command_id):
                        return candidate
            data = await get_guild_command(
                self.http,
                await self._application_id(),
                scope.guild_id,
                command_id,
            )
            result = from_payload({**data, "guild_id": str(scope.guild_id)})
            if use_cached:
                self._remote_command_registry.upsert(result)
            return result

        if use_cached:
            cached_command_list = await self._fetch_command_cached()
            for cached in cached_command_list[command_type].values():
                if str(cached.id) == str(command_id):
                    return cached
        data = await self.http.get_global_command(
            application_id=await self._application_id(), command_id=command_id
        )
        _result = from_payload(data)
        if use_cached:
            cache = self._fetch_interactions[command_type]
            for name, cached in list(cache.items()):
                if str(cached.id) == str(command_id) and name != _result.name:
                    del cache[name]
            cache[_result.name] = _result
        return _result

    async def _fetch_command_cached(
        self,
    ) -> dict[ApplicationCommandType, dict[str, command_types]]:
        if self._fetch_interactions is None:
            await self.fetch_commands()
        return self._fetch_interactions

    async def _sync_command(self, command: command_types):
        await self.wait_until_ready()
        if self._sync_policies.get(command.scope) is not None:
            return
        fetch_data = await self._fetch_command_cached()
        if command.name in fetch_data[command.type].keys():
            command_id = fetch_data[command.type][command.name].id
            if command.name in self._interactions[command.type]:
                self._interactions[command.type][command.name].id = command_id
            if not same_command_declaration(
                command, fetch_data[command.type][command.name]
            ):
                await self.edit_command(command=command)
        else:
            await self.register_command(command)
        return

    async def _sync_command_popping(self, command: command_types):
        await self.wait_until_ready()
        if self._sync_policies.get(command.scope) is not None:
            return
        fetch_data = await self._fetch_command_cached()
        if command.name in fetch_data[command.type].keys():
            command_id = fetch_data[command.type][command.name].id
            await self.delete_command(command, command_id=command_id)
        return

    # Extensions

    def _load_from_module_spec(
        self, spec: importlib.machinery.ModuleSpec, key: str, **kwargs
    ) -> None:
        # precondition: key not in self.__extensions
        lib = importlib.util.module_from_spec(spec)
        sys.modules[key] = lib
        try:
            spec.loader.exec_module(lib)  # type: ignore
        except Exception as e:
            del sys.modules[key]
            raise ExtensionFailed(key, e)

        try:
            setup = getattr(lib, "setup")
        except AttributeError:
            del sys.modules[key]
            raise NoEntryPointError(key)

        try:
            setup(self, **kwargs)
        except Exception as e:
            del sys.modules[key]
            raise ExtensionFailed(key, e) from e
        else:
            self.__extensions[key] = lib

    @staticmethod
    def _resolve_name(name: str, package: str | None) -> str:
        try:
            return importlib.util.resolve_name(name, package)
        except ImportError:
            raise ExtensionNotFound(name)

    def load_extension(
        self, name: str, *, package: str | None = None, **kwargs
    ) -> None:
        """Loads an extension.

        An extension is a python module that contains commands, cogs, or listeners.

        An extension must have a global function,
         setup defined as the entry point on what to do when the extension is loaded.
        This entry point must have a single argument, the bot.

        Parameters
        ----------
        name : str
            The extension name to load. It must be dot separated like regular Python imports if accessing a submodule.
            e.g. `foo.test` if you want to import `foo/test.py`.
        package : Optional[str]
            The package name to resolve relative imports with.
            This is required when loading an extension using a relative path,
            e.g `.foo.test.` Defaults to None.
        kwargs :
            Additional argument values to pass to predefined setup function.
        """
        name = self._resolve_name(name, package)
        if name in self.__extensions:
            raise ExtensionAlreadyLoaded(name)

        spec = importlib.util.find_spec(name)
        if spec is None:
            raise ExtensionNotFound(name)

        self._load_from_module_spec(spec, name, **kwargs)
        return

    def load_extensions(self, package: str, directory: str = None, **kwargs) -> None:
        """Fetches all extensions in the specified folder.
        They must have the setup function configured.

        Parameters
        ----------
        package :
            The package name to resolve relative imports with.
        directory : Optional[str]
            The path to the package address to read
            Usually takes an absolute path value.
        kwargs :
            Additional argument values to pass to predefined setup function.
        """
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
            self.load_extension(cog, **kwargs)
        return

    # Sync Command

    async def _sync_command_task(self):
        if len(self.__sync_command_before_ready_register) != 0:
            log.info(
                f"Register registered commands before bot is ready. List: "
                f"{', '.join([x.name for x in self.__sync_command_before_ready_register])}"
            )
        while len(self.__sync_command_before_ready_register) != 0:
            command = self.__sync_command_before_ready_register.pop()
            if self._sync_policies.get(command.scope) is not None:
                continue
            await self._sync_command(command=command)
        while len(self.__sync_command_before_ready_popping) != 0:
            command = self.__sync_command_before_ready_popping.pop()
            if self._sync_policies.get(command.scope) is not None:
                continue
            await self._sync_command_popping(command=command)

        if self.global_sync_command and self._sync_policies.get(GlobalScope()) is None:
            log.info(
                "global_sync_command is activated. Delete unregistered commands on client."
            )
            popping_data = await self._fetch_command_cached()
            for cmd_type in ApplicationCommandType:
                # Discord creates a default Activity entry point. Legacy global
                # deletion must not remove it without an explicit policy.
                if cmd_type is ApplicationCommandType.PRIMARY_ENTRY_POINT:
                    continue
                for already_cmd in self._interactions[cmd_type]:
                    if already_cmd in popping_data[cmd_type]:
                        del popping_data[cmd_type][already_cmd]

                for cmd in list(popping_data[cmd_type].values()):
                    await self.delete_command(cmd)

        await self._sync_configured_policies()

    async def _sync_configured_policies(self) -> None:
        """Run each configured scope once; failed scopes can retry on reconnect."""
        async with self._sync_policy_lock:
            for scope, policy in self._sync_policies.items():
                if scope in self._completed_sync_scopes:
                    continue
                result = await self.apply_sync_commands(scope, policy)
                if result.failures:
                    log.error(
                        "command synchronization failed for %s: %s",
                        scope,
                        result.failures,
                    )
                else:
                    self._completed_sync_scopes.add(scope)

    def add_detect_component(self, detect_component: DetectComponent, _parent=None):
        """Register for the detect_component event.

        When the user presses a specific button or makes a selection,
        the appropriate detect_component event for the custom_id is called.

        Parameters
        ----------
        detect_component: DetectComponent
            Coroutine functions that are called when a button is pressed or a selection is made.
        _parent
            These parameters is used for cog.
        """
        name = detect_component.custom_id
        if _parent is not None:
            detect_component.cog = _parent

        if name in self._detect_components:
            self._detect_components[name].append(detect_component)
        else:
            self._detect_components[name] = [detect_component]
        return

    def get_detect_component(self):
        """Get all of detect_components"""
        return self._detect_components

    def remove_detect_component(
        self, custom_id: str, detect_component: DetectComponent = None
    ):
        """Remove detect_component function.

        If detect_component is empty, all detect_components corresponding to the custom_id are deleted.

        Parameters
        ----------
        custom_id : str
            Custom_id value to detect. This can be a Button or a Selection.
        detect_component : Optional[DetectComponent]
            The detect_component function to delete, which defaults to None.
            If detect_component is None, delete all detect_components corresponding to custom_id.
        """
        if detect_component is None:
            self._detect_components.pop(custom_id)
        else:
            for i, x in enumerate(self._detect_components[custom_id]):
                if x == detect_component:
                    self._detect_components[custom_id].pop(i)
                    break
        return

    def add_interaction(
        self, command: decorator_command_types, sync_command: bool = None, _parent=None
    ):
        """Add interaction command to discord bot

        If sync_command is True,
        it will be synchronized with Discord and
        registered to a command in the Discord application if one does not exist.

        Parameters
        ----------
        command : Union[Command, MemberCommand, ContextMenuCommand]
            Application commands to register
        sync_command : Optional[bool]
            It synchronizes with Discord.
            If it's not in the Discord application command list,
            it will automatically add the command to the register_command function.

            The default value is None,
            which means that if it is None,
            it will follow the synchronization status ``global_sync_command`` attribute set by discord bot client.
        _parent
            These parameters is used for cog.

        Warnings
        --------
            If a command synchronization request is made before the Discord Bot is ready,
            it will wait and synchronize the command when it is ready.
        """
        if sync_command is None:
            sync_command = (
                self.global_sync_command
                and isinstance(command.scope, GlobalScope)
                and self._sync_policies.get(command.scope) is None
            )
        if self._sync_policies.get(command.scope) is not None:
            sync_command = False

        if (
            self._command_registry.get(command.scope, command.type, command.name)
            is not None
        ):
            raise CommandRegistrationError(command.name)

        if _parent is not None:
            command.cog = _parent

            # Add cog to subcommand in command's option.
            if getattr(command, "is_subcommand", False):
                for index, sub_command in enumerate(command.options):
                    if not isinstance(sub_command, (SubCommand, SubCommandGroup)):
                        continue
                    command.options[index].cog = command.cog

        if command.type == ApplicationCommandType.CHAT_INPUT:
            command.set_signature_option()
        self._command_registry.add(command)
        if isinstance(command.scope, GlobalScope):
            self._interactions[command.type][command.name] = command

        if sync_command:
            if self.is_ready():
                self._schedule_event(
                    self._sync_command, "sync_command", command=command
                )
            else:
                self.__sync_command_before_ready_register.append(command)
        return

    def add_activity_command(
        self,
        command: ActivityCommand,
        callback=None,
        *,
        sync_command: bool = False,
    ) -> ActivityBinding:
        """Register an Activity entry point and optional app-owned callback."""
        binding = ActivityBinding(command, callback)
        self.add_interaction(binding, sync_command=sync_command)
        return binding

    def get_interaction(self):
        """Get all interaction command included Application Command, User Command and Context Menu Command"""
        return self._command_registry.all()

    def set_sync_command(
        self, scope: GlobalScope | GuildScope, policy: SyncCommand
    ) -> None:
        """Set a runtime-only synchronization policy for one command scope."""
        self._sync_policies.set(scope, policy)
        self._completed_sync_scopes.discard(scope)

    def get_sync_command(self, scope: GlobalScope | GuildScope) -> SyncCommand | None:
        """Return the explicit policy, or None when automatic sync is disabled."""
        return self._sync_policies.get(scope)

    def remove_sync_command(self, scope: GlobalScope | GuildScope) -> None:
        """Stop automatic sync for a scope that had an explicit policy."""
        self._sync_policies.remove(scope)
        self._completed_sync_scopes.discard(scope)

    async def plan_sync_commands(self, scope: GlobalScope | GuildScope) -> SyncPlan:
        """Fetch remote declarations and preview one scope's exact changes."""
        if isinstance(scope, GlobalScope):
            await self.fetch_commands()
        elif isinstance(scope, GuildScope):
            await self.fetch_guild_commands(scope.guild_id)
        else:
            raise TypeError("scope must be GlobalScope or GuildScope")
        return plan_sync(scope, self._command_registry, self._remote_command_registry)

    async def apply_sync_commands(
        self,
        scope: GlobalScope | GuildScope,
        policy: SyncCommand | None = None,
    ) -> SyncResult:
        """Apply an explicitly supplied or configured policy to one scope."""
        active_policy = policy or self._sync_policies.get(scope)
        if active_policy is None:
            raise ValueError("SyncCommand policy is required to apply a sync plan")
        plan = await self.plan_sync_commands(scope)
        transport = CommandSyncAPI(self.http, await self._application_id())
        return await apply_sync_plan(plan, active_policy, transport)

    def delete_interaction(self, command: command_types, sync_command: bool = None):
        """Remove interaction command from discord bot

        If sync_command is True
        it will be synchronized with Discord and
        Delete the command if it exists in Discord.

        Parameters
        ----------
        command : Union[Command, MemberCommand, ContextMenuCommand]
            Application commands to delete
        sync_command : Optional[bool]
            It synchronizes with Discord.
            If it's not in the Discord application command list,
            it will automatically add the command to the delete_command function.

            The default value is None,
            which means that if it is None,
            it will follow the synchronization status ``global_sync_command`` attribute set by discord bot client.

        Warnings
        --------
            If a command synchronization request is made before the Discord Bot is ready,
            it will wait and synchronize the command when it is ready.
        """
        if sync_command is None:
            sync_command = (
                self.global_sync_command
                and isinstance(command.scope, GlobalScope)
                and self._sync_policies.get(command.scope) is None
            )
        if self._sync_policies.get(command.scope) is not None:
            sync_command = False

        if (
            self._command_registry.get(command.scope, command.type, command.name)
            is None
        ):
            raise CommandNotFound(f'Command "{command.name}" is not found')

        self._command_registry.remove(command)
        if isinstance(command.scope, GlobalScope):
            self._interactions[command.type].pop(command.name, None)

        if sync_command:
            if self.is_ready():
                self._schedule_event(
                    self._sync_command_popping, "sync_command", command=command
                )
            else:
                self.__sync_command_before_ready_popping.append(command)

    def add_interaction_cog(self, interaction_cog: T):
        """Add a "cog" to the bot.

        A cog is a class that has its own event listeners, detect_components and commands.

        Parameters
        ----------
        interaction_cog : type
            The cog to register to the bot.
        """
        self._interactions_of_group.append(interaction_cog)
        for func, attr in inspect.getmembers(interaction_cog):
            if isinstance(attr, BaseCommand):
                attr: decorator_command_types
                self.add_interaction(attr, attr.sync_command, interaction_cog)
            elif isinstance(attr, DetectComponent):
                self.add_detect_component(attr, interaction_cog)
            elif inspect.iscoroutinefunction(attr):
                if hasattr(attr, "__cog_listener__") and hasattr(
                    attr, "__cog_listener_names__"
                ):
                    if not attr.__cog_listener__:
                        continue
                    for name in attr.__cog_listener_names__:
                        self.add_listener(attr, name=name)
        return

    # Gateway event hooks
    def _install_interaction_parsers(self) -> None:
        """Route ``INTERACTION_CREATE`` / ``MESSAGE_CREATE`` into this extension's
        own context objects.

        Wraps :attr:`discord.state.ConnectionState.parsers`, so ``data`` is already
        decompressed and JSON-decoded. The library's own parser is still called,
        keeping :class:`discord.Interaction`, the view/modal stores and
        ``on_interaction`` working.
        """
        state: ConnectionState = self._connection
        for event, extra in (
            ("INTERACTION_CREATE", self._parse_interaction_create),
            ("MESSAGE_CREATE", self._parse_message_create),
        ):
            state.parsers[event] = self._chain_parser(state.parsers.get(event), extra)

    @staticmethod
    def _chain_parser(original, extra):
        def parser(data: dict) -> None:
            if original is not None:
                original(data)
            try:
                extra(data)
            except Exception:
                log.exception(
                    "discord.ext.interaction failed to process a gateway event"
                )

        return parser

    def _parse_interaction_create(self, data: dict) -> None:
        self._interaction_dispatcher().route(data)

    def _interaction_dispatcher(self) -> InteractionDispatcher:
        return InteractionDispatcher(
            self,
            self._connection.dispatch,
            {
                2: ApplicationContext,
                3: ComponentsContext,
                4: AutocompleteContext,
                5: ModalSubmitContext,
            },
        )

    def _parse_message_create(self, data: dict) -> None:
        state: ConnectionState = self._connection
        channel, _ = state._get_guild_channel(data)
        message = Message(state=state, data=data, channel=channel)
        state.dispatch("interaction_message", message)

    # Application Context
    async def process_interaction(self, ctx: ApplicationContext):
        _state: ConnectionState = self._connection
        command_type = ApplicationCommandType(ctx.application_type)
        scope = (
            GuildScope(int(ctx.guild_id))
            if getattr(ctx, "guild_id", None)
            else GlobalScope()
        )
        command = self._command_registry.get(
            scope,
            command_type,
            ctx.name,
            fallback_global=True,
        ) or self._interactions[command_type].get(ctx.name)
        if command is None:
            return

        _state.dispatch("command", ctx)

        try:
            func = ctx.function = command
            if command.cog is not None:
                ctx.parents = command.cog

            if await self.can_run(ctx):
                _option = {}
                if ctx.application_type == ApplicationCommandType.CHAT_INPUT.value:
                    _option = ctx.options
                    is_subcommand = getattr(command, "is_subcommand", False)
                    if is_subcommand:
                        options = command.options
                        selected_options = ctx.options
                        if "subcommand_group" in ctx.options:
                            sub_command_group = ctx.options["subcommand_group"]
                            selected_options = sub_command_group.options
                            for opt in command.options:
                                if (
                                    isinstance(opt, SubCommandGroup)
                                    and sub_command_group.name == opt.name
                                ):
                                    options = opt.options
                                    break
                        sub_command = selected_options["subcommand"]
                        for opt in options:
                            if opt.name == sub_command.name and isinstance(
                                opt, SubCommand
                            ):
                                ctx.function = func = opt
                                ctx.parents = None
                                if opt.cog is not None:
                                    ctx.parents = opt.cog
                                _option = sub_command.options
                                break
                if await func.can_run(ctx):
                    if ctx.application_type == ApplicationCommandType.CHAT_INPUT.value:
                        for f_opt in copy.copy(_option).keys():
                            for opt in func.options:
                                if opt.name == f_opt and opt.parameter_name != f_opt:
                                    _option[opt.parameter_name] = _option.pop(f_opt)
                                elif opt.name == f_opt:
                                    break
                        await func.callback(ctx, **_option)
                    else:
                        await func.callback(ctx)
                else:
                    raise CheckFailure("The check functions for command failed.")
            else:
                raise CheckFailure("The global check once functions failed.")
        except Exception as error:
            if isinstance(error, CheckFailure):
                _state.dispatch("command_permission_error", ctx, error)
            _state.dispatch("interaction_command_error", ctx, error)
            raise error
        else:
            _state.dispatch("command_complete", ctx)
        return

    async def on_interaction_command(self, ctx: ApplicationContext):
        await self.process_interaction(ctx)
        return

    async def on_components(self, ctx: ComponentsContext):
        await self.process_components(ctx)
        return

    # Components
    def wait_for_component(
        self, custom_id: str, check=None, timeout=None
    ) -> _Coroutine[ComponentsContext]:
        """Wait for the component with the specified custom_id to be sent.

        The ``timeout`` parameter is passed to :func:`asyncio.wait_for()`.
        Note that by default it will not time out; if it does,
        it will propagate an :exc:`asyncio.TimeoutError`, which is provided for ease of use.

        Parameters
        ----------
        custom_id : str
            Custom ID for detect component
        check : Optional[Callable[..., bool]]
            A predicate to check what to wait for.
            The arguments must meet the parameters of the event being waited for.
        timeout : Optional[float]
            The number of seconds to wait before timing out and raising :exc:`asyncio.TimeoutError`.

        Returns
        -------
            Returns a `ComponentsContext` that satisfies the custom_id.
        """
        future = asyncio.get_running_loop().create_future()
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

        listeners.append((future, check, False))
        return asyncio.wait_for(future, timeout)

    def wait_for_global_component(
        self, check=None, timeout=None
    ) -> _Coroutine[ComponentsContext]:
        """Unconstrained by custom_id, waits for any component_id.

        The ``timeout`` parameter is passed to :func:`asyncio.wait_for()`.
        Note that by default it will not time out; if it does,
        it will propagate an :exc:`asyncio.TimeoutError`, which is provided for ease of use.

        Parameters
        ----------
        check : Optional[Callable[..., bool]]
            A predicate to check what to wait for.
            The arguments must meet the parameters of the event being waited for.
        timeout : Optional[float]
            The number of seconds to wait before timing out and raising :exc:`asyncio.TimeoutError`.

        Returns
        -------
            Returns a :class:`ComponentContext` that satisfies the condition on `check`.
        """
        future = asyncio.get_running_loop().create_future()
        if check is None:

            def _check(_: ComponentsContext):
                return True

            check = _check

        self._deferred_global_components.append((future, check, True))
        return asyncio.wait_for(future, timeout)

    async def can_run(self, ctx: ApplicationContext | ComponentsContext) -> bool:
        data = self._checks
        if len(data) == 0:
            return True

        return await async_all(f(ctx) for f in data)  # type: ignore

    async def process_components(self, component: ComponentsContext):
        _state: ConnectionState = self._connection

        detect_component = self._detect_components.get(component.custom_id)
        if detect_component is None:
            detect_component = []
        active_component = []
        for _component in detect_component:
            if (
                _component.type_id == component.component_type
                or _component.type is None
            ):
                try:
                    if await self.can_run(component):
                        if await _component.can_run(component):
                            await _component.callback(component)
                    else:
                        raise CheckFailure("The global check once functions failed.")
                except Exception as error:
                    if isinstance(error, CheckFailure):
                        _state.dispatch("component_permission_error", component, error)
                    _state.dispatch("component_error", component, error)
                else:
                    _state.dispatch("component_complete", component)
                    active_component.append(component)

        listeners = copy.copy(self._deferred_global_components)
        listeners += copy.copy(self._deferred_components.get(component.custom_id, []))
        detect_component_wait_for = []
        if len(listeners) > 0:
            removed = []
            global_removed = []
            for index, (future, check, global_component) in enumerate(listeners):
                if future.cancelled():
                    if global_component:
                        global_removed.append(index)
                    else:
                        removed.append(index)
                    continue

                try:
                    result = check(component)
                except Exception as exc:
                    future.set_exception(exc)
                    if global_component:
                        global_removed.append(index)
                    else:
                        removed.append(index)
                else:
                    if result:
                        detect_component_wait_for.append(component)
                        future.set_result(component)
                        if global_component:
                            global_removed.append(index)
                        else:
                            removed.append(index)

            if len(removed) == len(listeners):
                self._deferred_components.pop(component.custom_id)
            else:
                for idx in reversed(removed):
                    self._deferred_components.get(component.custom_id, []).pop(idx)

            for idx in reversed(global_removed):
                self._deferred_global_components.pop(idx)
        if len(detect_component_wait_for) == 0 and len(active_component) == 0:
            _state.dispatch("components_cancelled", component)
        return


class Client(ClientBase, discord.Client):
    pass


class AutoShardedClient(ClientBase, discord.AutoShardedClient):
    pass
