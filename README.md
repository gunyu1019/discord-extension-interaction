<h1 align="center">Discord Extension Interaction</h1>
<p align="center">
    <img src="https://img.shields.io/badge/release_version-0.5.2%20beta-0080aa?style=flat" alt="Release" >
</p>

# Introduce
Slash Command is supported through [discord.py](https://github.com/Rapptz/discord.py). <br/>
Based on discord.ext.commands, compatible with existing frames.


#### Compatibility list
<table>
    <thead>
        <tr>
            <th>Moudle Name</th>
            <th>Version</th>
            <th>Tested</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><a href="https://github.com/Rapptz/discord.py">discord.py</a></td>
            <td>v1.7.3</td>
            <td>✔️</td>
        </tr>
        <tr>
            <td><a href="https://github.com/Rapptz/discord.py">discord.py</a></td>
            <td>v2.0.0 (alpha)</td>
            <td>✔️</td>
        </tr>
        <tr>
            <td><a href="https://github.com/Pycord-Development/pycord">pycord</a></td>
            <td>v1.7.3</td>
            <td>✔️</td>
        </tr>
        <tr>
            <td><a href="https://github.com/Pycord-Development/pycord">pycord</a></td>
            <td>v2.0.0 (beta)</td>
            <td>⚠️</td>
        </tr>
        <tr>
            <td><a href="https://github.com/nextcord/nextcord">nextcord</a></td>
            <td>v2.0.0a6</td>
            <td>✔️</td>
        </tr>
        <tr>
            <td><a href="https://github.com/iDevision/enhanced-discord.py">Enhanced-discord.py</a></td>
            <td>v1.7.3.7.post6</td>
            <td>✔️</td>
        </tr>
        <tr>
            <td><a href="https://github.com/DisnakeDev/disnake">disnake</a></td>
            <td>v2.3.0 (beta)</td>
            <td>❌️</td>
        </tr>
    </tbody>
</table>

* confirmed that the framework is integrated in py-cord v2.0. (add_listener not working) [#1](https://github.com/gunyu1019/discord-extension-interaction/issues/1)
* disnake is incompatible with different package names.

# Installing
**Python 3.7 or higher is required.**<br/>

To install the library without full voice support, you can just run the following command:
```commandline
# Linux/macOS
python3 -m pip install -U discord-extension-interaction
# Windows
py -3 -m pip install -U discord-extension-interaction
```

To install the development version, do the following:
```bash
$ git clone https://github.com/gunyu1019/discord-extension-interaction
$ cd discord.py
$ python3 -m pip install -U .
```

# Quick Example
```python
from discord.ext import interaction
from discord import Intents

# You can also set the command_prefix value to None. Just the original framework will not work.
intents = Intents.default()
bot = interaction.Client(global_sync_command=True, intents = intents)
@interaction.command(description="This is ping")
async def ping(ctx: interaction.ApplicationContext):
    await ctx.send("pong!")
    return
bot.add_interaction(ping)
bot.run("< TOKEN >")
```