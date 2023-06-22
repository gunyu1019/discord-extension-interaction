import discord
from discord.ext import interaction

intents = discord.Intents.default()
client = interaction.Client(global_sync_command=True, intents=intents)


@interaction.command(
    name="component_test", description="This command is component test."
)
async def component_test(ctx: interaction.ApplicationContext):
    await ctx.send(
        "Press the button below the message.",
        components=[
            interaction.ActionRow(
                components=[
                    interaction.Button(
                        label="button1",
                        custom_id="wait_for_component_button",
                        style=discord.ButtonStyle.primary,
                    ),
                    interaction.Button(
                        label="button2",
                        custom_id="event_button",
                        style=discord.ButtonStyle.secondary,
                    ),
                ]
            )
        ],
    )
    result: interaction.ComponentsContext = await client.wait_for_component(
        "wait_for_component_button"
    )
    await result.send("{0} pressed the first button.".format(result.author.mention))
    return


@interaction.detect_component()
async def creative(ctx: interaction.ComponentsContext):
    await ctx.send("{0} pressed the second button.".format(ctx.author.mention))
    return


@client.listen()
async def on_components_cancelled(ctx):
    await ctx.send("button is not found.")
    return


client.add_interaction(component_test, sync_command=True)
client.run("token")
