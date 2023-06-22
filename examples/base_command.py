import discord
import datetime
from discord.ext import interaction


intents = discord.Intents.default()
client = interaction.Client(global_sync_command=True, intents=intents)


@interaction.command(name="ping", description="Receive ping")
async def ping(ctx: interaction.ApplicationContext):
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    await ctx.send(
        f"Pong, received time: {now - ctx.created_at} or {ctx.created_at - now}"
    )
    return


client.add_interaction(ping, sync_command=True)
client.run("token")
