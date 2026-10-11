"""Old import paths remain aliases while source lives in two packages."""

from importlib import import_module

from discord.ext import interaction


def test_legacy_modules_alias_model_and_implementation_modules():
    package = "discord.ext.interaction"
    replacements = {
        "commands": "models.commands",
        "client": "implementation.client",
        "interaction": "implementation.interaction",
        "domain.component": "models.component",
        "legacy_components.button": "models.legacy_button",
        "application.sync_planner": "implementation.sync_planner",
        "serialization.components": "models.component_codec",
        "transport.interaction_api": "implementation.interaction_api",
    }
    for old, new in replacements.items():
        assert import_module(f"{package}.{old}") is import_module(f"{package}.{new}")

    assert interaction.Client is import_module(f"{package}.client").Client
    assert interaction.Button is import_module(f"{package}.legacy_components.button").Button
    assert interaction.client is import_module(f"{package}.client")
    assert interaction.commands is import_module(f"{package}.commands")
