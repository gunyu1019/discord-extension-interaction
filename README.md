<h1 align="center">Discord Extension Interaction</h1>
<p align="center">
    <img src="https://img.shields.io/pypi/v/discord-extension-interaction?style=flat" alt="Release" >
    <img src="https://img.shields.io/pypi/dm/discord-extension-interaction?style=flat" alt="Release" >
    <img src="https://img.shields.io/pypi/l/discord-extension-interaction?style=flat" alt="Release" >
</p>

# Introduce
Slash Command is supported through [discord.py](https://github.com/Rapptz/discord.py). <br/>
Based on discord.ext.commands, compatible with existing frames.


#### Compatibility list
<table>
    <thead>
        <tr>
            <th>Module</th>
            <th>Supported version</th>
            <th>Local test</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><a href="https://github.com/Rapptz/discord.py">discord.py</a></td>
            <td>&gt;=2.7.1,&lt;3</td>
            <td>2.7.1</td>
        </tr>
        <tr>
            <td><a href="https://github.com/Pycord-Development/pycord">Pycord</a></td>
            <td>Not supported</td>
            <td>—</td>
        </tr>
    </tbody>
</table>

The package uses `discord.py`; Pycord is outside the supported dependency range.

# Installing
**Python 3.10 or higher is required.** The project CI runs on Python 3.10–3.13.<br/>

Install the library and its `discord.py` dependency with:
```commandline
# Linux/macOS
python3 -m pip install -U discord-extension-interaction

# Windows
py -3 -m pip install -U discord-extension-interaction
```

The `[discordpy]` extra is retained for existing install commands. `discord.py` is
already a required dependency.
```commandline
# Linux/macOS
python3 -m pip install -U discord-extension-interaction[discordpy]

# Windows
py -3 -m pip install -U discord-extension-interaction[discordpy]
```

For HTTP interaction webhooks, install the signing extra:

```commandline
python -m pip install -U 'discord-extension-interaction[http]'
```

HTTP-only receiving does not connect to the Gateway, so call `await bot.login(token)`
before serving requests (and `await bot.close()` on shutdown). See
[new feature examples](docs/new-feature-examples.md#aiohttp-수신) for a complete setup.

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
bot = interaction.Client(global_sync_command=True, intents=intents)


@interaction.command(description="This is ping")
async def ping(ctx: interaction.ApplicationContext):
    await ctx.send("pong!")

bot.add_interaction(ping)
bot.run("TOKEN")
```

You can find more examples in the [examples](https://github.com/gunyu1019/discord-extension-interaction/tree/main/examples) directory.

The current [Discord API support matrix](docs/current-support.md) and
[new feature examples](docs/new-feature-examples.md) show Components V2, modal
inputs, HTTP receiving, Activity commands, and command permissions. See the
[changelog](CHANGELOG.md) and the [0.6 to 0.8 migration guide](docs/migration-0.6-to-0.8.md)
when upgrading, and the [implementation plan](docs/implementation-plan.md) for how
the support was built.
