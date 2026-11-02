# Changelog

All notable changes to this project are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.8.0] - Unreleased

Compared with 0.6.2. See the [migration guide](docs/migration-0.6-to-0.8.md) for upgrade steps.

### Added

- Components V2: `Section`, `TextDisplay`, `Thumbnail`, `MediaGallery` (with `MediaGalleryItem`),
  `File`, `Separator`, `Container` and `UnfurledMediaItem`. The `IS_COMPONENTS_V2` flag is set when
  a message contains a V2 component, and the 40-component and field rules are validated before sending.
- Automatic select menus `UserSelect`, `RoleSelect`, `MentionableSelect` and `ChannelSelect`, with
  `SelectDefaultValue` and resolved objects on `ComponentsContext`.
- Modal components: `Label`, `FileUpload`, `RadioGroup`, `CheckboxGroup` and `Checkbox`; select menus in
  modals; `ModalSubmitContext.get_component`, `get_resolved_values` and `file_uploads`.
- Premium buttons through `Button(style=premium, sku_id=...)`.
- Unknown component types are kept as `UnknownComponent` instead of being dropped.
- Command scopes (`GlobalScope`, `GuildScope`), guild command REST operations, name and description
  localizations, `nsfw`, `default_member_permissions`, `integration_types` and `contexts` on command
  decorators, and per-scope `SyncCommand(create, edit, delete)` policies with
  `Client.plan_sync_commands` / `apply_sync_commands`.
- Activity entry point commands (`ActivityCommand`, `Client.add_activity_command`) and
  `ctx.launch_activity()`.
- `CommandPermissionsAPI` for per-command guild permissions.
- HTTP outgoing webhook receiving with `AiohttpInteractionAdapter` (`[http]` extra): Ed25519 signature
  verification, PING/PONG, `202` callbacks or inline JSON responses.
- Interaction metadata on every context: `envelope`, `app_permissions`, `context`,
  `authorizing_integration_owners`, `entitlements` and `attachment_size_limit`.
- `ctx.callback_response`, `InteractionHTTPClient.get_followup`, `silent` and `poll` on
  `InteractionContext.send`, and `poll` on `InteractionContext.edit`.

### Changed

- `discord.py>=2.7.1,<3` is now a required dependency (it was only an optional extra). Python 3.10 or
  newer is still required.
- Interactions are received through `ConnectionState` parser hooks. The client no longer forces
  `enable_debug_events=True` and no longer decompresses the raw socket stream itself.
- `InteractionContext.send` requests the initial callback with `with_response=true` and reads the
  created message from it instead of issuing `GET @original`.
- `ctx.launch_activity()` returns the Interaction Callback Response instead of `None`.
- `TextInput.label` is optional (it must be omitted inside a `Label`); `Selection` accepts `required`.
- When the guild is not cached, `ctx.channel` is a `PartialMessageable` with an integer ID, the guild
  ID and the channel type taken from the payload.
- Commands with a guild scope are sent to the guild endpoints. Previously the guild ID was stored but
  the request always went to the global endpoint.
- Discord internals used from discord.py are imported through `discord.ext.interaction.dpy_internal`.

### Removed

- `ModalContext` (renamed to `ModalSubmitContext`).
- `MessageCommand` (deprecated since 0.1) and `MessageSendable` (use `MessageTransferable`).
- `ClientBase.on_socket_raw_receive`, `http.handler_message_parameter` and `http.MultipartParameters`.

### Fixed

- Guild interactions raised `TypeError` when the guild was not cached (HTTP-only receiving,
  user-installed apps in guilds the bot has not joined, clients without the guilds intent). The author
  is now a `discord.User` built from the member payload, and Role options no longer require a cached guild.
- The HTTP webhook adapter no longer echoes handler error messages in its `500` body.
- `SelectOption` no longer sends `"default": false` for every option.
- `nsfw` is part of the command registration payload.
- Sub-command groups, same-`custom_id` components of different types, Mentionable and Attachment
  command options, and setup-hook removal behave as documented.
