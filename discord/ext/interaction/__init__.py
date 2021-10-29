import discord
import zlib
from discord.ext import commands
from discord.utils import _from_json


class Client(commands.bot.BotBase, discord.Client):
    def __init__(self, command_prefix, **options):
        super().__init__(command_prefix, **options)
        self._buffer = bytearray()
        self._zlib = zlib.decompressobj()

    async def on_socket_raw_receive(self, msg):
        if type(msg) is bytes:
            self._buffer.extend(msg)

            if len(msg) < 4 or msg[-4:] != b'\x00\x00\xff\xff':
                return

            msg = self._zlib.decompress(self._buffer)
            msg = msg.decode('utf-8')
            self._buffer = bytearray()
        payload = _from_json(msg)

        data = payload.get("d", {})
        t = payload.get("t", "")
        op = payload.get("op", "")

        state = self._connection


class AutoShardedClient(Client, discord.AutoShardedClient):
    pass
