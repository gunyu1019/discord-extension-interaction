import discord
import datetime
from discord.ext import interaction

intents = discord.Intents.default()
client = interaction.Client(global_sync_command=True, intents=intents)


class InteractionCommandOfGroup:
    def __init__(self, _client):
        self.client = _client

    @interaction.command(name="ping", description="Receive ping")
    async def ping(self, ctx: interaction.ApplicationContext):
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        await ctx.send(
            f"Pong, received time: {now - ctx.created_at} or {ctx.created_at - now}"
        )
        return

    @interaction.listener()
    async def on_ready(self):
        print("Ready")


client.add_interaction_cog(InteractionCommandOfGroup)
client.run("token")
