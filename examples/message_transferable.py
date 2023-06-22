import discord
from discord.ext import interaction

intents = discord.Intents.default()
client = interaction.Client(global_sync_command=True, intents=intents)


@client.listen()
async def on_message(original_message: discord.Message):
    message = interaction.MessageTransferable(
        state=getattr(original_message, "_state"), channel=original_message.channel
    )
    await message.send("Hello Message?")
    return


client.run("token")
