<h1 align="center">Discord Extension Interaction</h1>
<p align="center">
    <img src="https://img.shields.io/badge/release_version-0.6.0%20beta-0080aa?style=flat" alt="Release" >
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
            <td>v2.3.0</td>
            <td>✔️</td>
        </tr>
        <tr>
            <td><a href="https://github.com/Pycord-Development/pycord">Pycord</a></td>
            <td>v2.4.1</td>
            <td>❌</td>
        </tr>
    </tbody>
</table>

* Plans to support py-cord, but `discord-extension-interaction` is not supported now.

# Installing
**Python 3.9 or higher is required.**<br/>

To install the library without full voice support, you can just run the following command:
```commandline
# Linux/macOS
python3 -m pip install -U discord-extension-interaction

# Windows
py -3 -m pip install -U discord-extension-interaction
```

To install the library with discord.py
```commandline
# Linux/macOS
python3 -m pip install -U discord-extension-interaction[discordpy]

# Windows
py -3 -m pip install -U discord-extension-interaction[discordpy]
```

To install the development version, do the following:
```bash
$ git clone https://github.com/gunyu1019/discord-extension-interaction
$ cd discord-extension-interaction
$ python3 -m pip install -U .
```

# Quick Example
```python
from discord.ext import interaction
from discord import Intents

intents = Intents.default()
bot = interaction.Client(global_sync_command=True, intents = intents)


@interaction.command(description="This is ping")
async def ping(ctx: interaction.ApplicationContext):
    await ctx.send("pong!")
    return

bot.add_interaction(ping)
bot.run("TOKEN")
```

You can find more examples in the [examples](https://github.com/gunyu1019/discord-extension-interaction/tree/main/examples) directory.
