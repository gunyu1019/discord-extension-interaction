"""Compare only fields declared for an application command."""


def same_command_declaration(local, remote) -> bool:
    """Ignore Discord-assigned ID/version while keeping scope and payload fields."""
    return (str(local.guild_id) if local.guild_id is not None else None) == (
        str(remote.guild_id) if remote.guild_id is not None else None
    ) and local.to_register_dict() == remote.to_register_dict()
