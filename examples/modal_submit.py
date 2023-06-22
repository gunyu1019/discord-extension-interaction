import discord
from discord.ext import interaction


intents = discord.Intents.default()
client = interaction.Client(global_sync_command=True, intents=intents)


@interaction.command(name="modal", description="Modal Test.")
async def modal(ctx: interaction.ApplicationContext):
    await ctx.modal(
        "modal_test",
        "Modal Title",
        components=[
            interaction.ActionRow(
                components=[
                    interaction.TextInput(
                        custom_id="text-input1", style=1, label="Short Text"
                    )
                ]
            ),
            interaction.ActionRow(
                components=[
                    interaction.TextInput(
                        custom_id="text-input2",
                        style=2,
                        label="Long Text",
                        max_length=4000,
                    )
                ]
            ),
        ],
    )
    return


@client.listen()
async def on_modal(ctx: interaction.ModalContext):
    await ctx.send(
        f"Short Text: {ctx.components[0].value}\n"
        f"Long Text: {ctx.components[1].value}"
    )
    return


client.add_interaction(modal, sync_command=True)
client.run("token")
