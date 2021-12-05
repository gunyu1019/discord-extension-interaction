<h1 align="center">Discord(Py)-Extension-Cog</h1>
<p align="center">
    <img src="https://img.shields.io/badge/release_version-0.1.1%20alpha-0080aa?style=flat" alt="Release" >
</p>

# Introduce
[discord.py](https://github.com/Rapptz/discord.py)의 [ext.commands](https://github.com/Rapptz/discord.py/tree/master/discord/ext/commands)와 비슷한 구조를 갖고 있으며, 빗금 명령어(Slash Command)와 일반 명령어(Message Command)를 한 번에 사용할 수 있도록 만들어 주는 확장 모듈입니다.


```py
import discord
from discord.ext import interaction
from discord.ext.interaction.commands import CommandOption

client = interaction.Client(command_prefix="=", global_sync_command=True)


@interaction.command()
def ping1(argument: int, channel: discord.TextChannel = None):
  return

@interaction.command(
  options=[CommandOption(description="옵션 설명")]
)
def ping2(argument: int, channel: discord.TextChannel = None):
  return

@interaction.command(
    description="This is argument test.",
)
@interaction.option(description="This is option test.")
@interaction.option(min_value=0, max_value=25565)
@interaction.option(channel_type=discord.ChannelType.text)
@interaction.permissions(
    id=916798717208694836,
    guild_id=844613188900356157,
    type=interaction.PermissionType.USER,
    permission=True
)
@interaction.has_role(item=844620432904552539, exception=False)
async def ping3(
        ctx,
        argument1: discord.User,
        argument2: int = None,
        argument3: discord.TextChannel = None,
):
    await ctx.send(
        "{0}님은 {1}와 {2}를 택하였습니다.".format(argument1, argument2, argument3)
    )
    return


client.add_interaction(ping1, sync_command=True)
client.add_interaction(ping2, sync_command=True)
client.add_interaction(ping3, sync_command=True)

client.run('token')
```