"""New select classes can constrain callbacks by Discord component type."""

import asyncio
from types import SimpleNamespace

from discord.ext import interaction


def test_auto_select_decorator_filters_by_type(offline_client):
    called = []

    @interaction.detect_component(custom_id="pick", component_type=interaction.UserSelect)
    async def on_user(ctx):
        called.append(ctx.component_type)

    offline_client.add_detect_component(on_user)
    asyncio.run(offline_client.process_components(SimpleNamespace(
        custom_id="pick", component_type=interaction.RoleSelect.TYPE
    )))
    asyncio.run(offline_client.process_components(SimpleNamespace(
        custom_id="pick", component_type=interaction.UserSelect.TYPE
    )))
    assert called == [5]


def test_wait_for_component_receives_new_select(offline_client):
    async def run():
        waiter = asyncio.create_task(offline_client.wait_for_component("pick", timeout=1))
        await asyncio.sleep(0)
        context = SimpleNamespace(custom_id="pick", component_type=interaction.ChannelSelect.TYPE)
        await offline_client.process_components(context)
        return await waiter

    assert asyncio.run(run()).component_type == 8
