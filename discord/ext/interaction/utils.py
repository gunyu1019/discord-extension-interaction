"""MIT License

Copyright (c) 2021 gunyu1019

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
import inspect
import discord

try:
    import orjson
except ModuleNotFoundError:
    HAS_ORJSON = False
else:
    HAS_ORJSON = True


if HAS_ORJSON:
    _from_json = orjson.loads
else:
    _from_json = json.loads


channel_types = [
    discord.TextChannel,
    discord.VoiceChannel,
    discord.DMChannel,
    discord.StageChannel,
    discord.GroupChannel,
    discord.CategoryChannel,
    discord.StoreChannel
]


try:
    from deprecated import deprecated
except ModuleNotFoundError:
    def deprecated(*_1, **_2):
        def decorator(func):
            return func
        return decorator


def get_as_snowflake(data, key):
    try:
        value = data[key]
    except KeyError:
        return None
    else:
        return value and int(value)


def get_enum(cls, val):
    enum_val = [i for i in cls if i.value == val]
    if len(enum_val) == 0:
        return val
    return enum_val[0]


def _files_to_form(files: list, payload: dict):
    form = [{'name': 'payload_json', 'value': to_json(payload)}]
    if len(files) == 1:
        file = files[0]
        form.append(
            {
                'name': 'file',
                'value': file.fp,
                'filename': file.filename,
                'content_type': 'application/octet-stream',
            }
        )
    else:
        for index, file in enumerate(files):
            form.append(
                {
                    'name': f'file{index}',
                    'value': file.fp,
                    'filename': file.filename,
                    'content_type': 'application/octet-stream',
                }
            )
    return form


def _allowed_mentions(state, allowed_mentions):
    if allowed_mentions is not None:
        if state.allowed_mentions is not None:
            allowed_mentions = state.allowed_mentions.merge(allowed_mentions).to_dict()
        else:
            allowed_mentions = allowed_mentions.to_dict()
    else:
        allowed_mentions = state.allowed_mentions and state.allowed_mentions.to_dict()
    return allowed_mentions


def to_json(obj):
    return json.dumps(obj, separators=(',', ':'), ensure_ascii=True)


async def async_all(gen, *, check=inspect.isawaitable):
    for elem in gen:
        if check(elem):
            elem = await elem
        if not elem:
            return False
    return True
