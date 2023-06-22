import discord
import datetime
from discord.ext import interaction


intents = discord.Intents.default()
client = interaction.Client(global_sync_command=True, intents=intents)


@interaction.command(name="mention", description="This command mention another user.")
async def mention(
    ctx: interaction.ApplicationContext, mention: interaction.Mentionable
):
    await ctx.send(f"Hello? {mention}")
    return


client.add_interaction(mention, sync_command=True)
client.run("token")
