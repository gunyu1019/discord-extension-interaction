"""A component handler's declared type must constrain custom_id dispatch."""

import asyncio
from types import SimpleNamespace

from discord.ext import interaction


def test_detect_component_type_id_uses_declared_class():
    @interaction.detect_component(custom_id="shared", component_type=interaction.Button)
    async def on_button(_ctx):
        pass

    assert on_button.type_id == interaction.Button.TYPE


def test_same_custom_id_dispatches_only_to_matching_component_type(offline_client):
    called = []

    @interaction.detect_component(custom_id="shared", component_type=interaction.Button)
    async def on_button(_ctx):
        called.append("button")

    @interaction.detect_component(custom_id="shared", component_type=interaction.Selection)
    async def on_select(_ctx):
        called.append("select")

    offline_client.add_detect_component(on_button)
    offline_client.add_detect_component(on_select)

    asyncio.run(offline_client.process_components(SimpleNamespace(
        custom_id="shared", component_type=interaction.Button.TYPE
    )))
    assert called == ["button"]

    asyncio.run(offline_client.process_components(SimpleNamespace(
        custom_id="shared", component_type=interaction.Selection.TYPE
    )))
    assert called == ["button", "select"]
