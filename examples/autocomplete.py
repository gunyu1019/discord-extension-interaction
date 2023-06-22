import discord
from discord.ext import interaction

intents = discord.Intents.default()
client = interaction.Client(global_sync_command=True, intents=intents)


@interaction.command(
    description="AutoComplete Test Command",
)
@interaction.option(
    name="argument", description="This is option test.", autocomplete=True
)
async def autocomplete(ctx: interaction.ApplicationContext, argument: str):
    await ctx.send(f"You picked {argument}!")
    return


@client.listen()
async def on_autocomplete(context: interaction.AutocompleteContext):
    if context.name != "autocomplete":
        return
    await context.autocomplete(
        choices=[
            interaction.CommandOptionChoice(name="Hello", value="pick-1"),
            interaction.CommandOptionChoice(name="Bye", value="pick-2"),
        ]
    )
    return


client.add_interaction(autocomplete, sync_command=True)
client.run("token")
