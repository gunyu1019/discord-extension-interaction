"""SyncPlan exposes create, edit, delete and unchanged candidates per scope."""

from discord.ext import interaction
from discord.ext.interaction.command_registry import CommandRegistry
from discord.ext.interaction.sync_planner import SyncOperation, plan_sync


def test_sync_plan_classifies_commands_and_keeps_guilds_separate():
    scope = interaction.GuildScope(42)
    local = CommandRegistry()
    remote = CommandRegistry()
    local.add(interaction.SlashCommand(name="create", description="New", scope=scope))
    local.add(interaction.SlashCommand(name="edit", description="New", scope=scope))
    local.add(interaction.SlashCommand(name="keep", description="Same", scope=scope))
    remote.add(interaction.SlashCommand(name="delete", description="Old", scope=scope))
    remote.add(interaction.SlashCommand(name="edit", description="Old", scope=scope))
    remote.add(interaction.SlashCommand(name="keep", description="Same", scope=scope))
    remote.add(interaction.SlashCommand(
        name="other", description="Other", scope=interaction.GuildScope(99),
    ))
    plan = plan_sync(scope, local, remote)
    assert [(item.key.name, item.operation) for item in plan.items] == [
        ("create", SyncOperation.CREATE),
        ("delete", SyncOperation.DELETE),
        ("edit", SyncOperation.EDIT),
        ("keep", SyncOperation.UNCHANGED),
    ]
    assert [item.key.name for item in plan.candidates(SyncOperation.DELETE)] == ["delete"]
