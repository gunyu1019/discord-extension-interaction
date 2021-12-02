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


@client.command()
def ping1(argument: int, channel: discord.TextChannel = None):
  return

@client.command(
  options=[CommandOption(description="옵션 설명")]
)
def ping2(argument: int, channel: discord.TextChannel = None):
  return


client.add_interaction(ping1, sync_command=True)
client.add_interaction(ping2, sync_command=True)

client.run('token')
```