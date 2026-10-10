"""Send, verify, and optionally retain a Components V2 test message."""

import argparse
import asyncio
from io import BytesIO

import discord
from discord.ext import interaction

from live_smoke_commands import load_local_env, required


def message_components(image_url: str):
    media = interaction.UnfurledMediaItem(image_url)
    container = interaction.Container(
        [
            interaction.Section(
                [interaction.TextDisplay("## Codex smoke test")],
                interaction.Thumbnail(media, description="Bot avatar"),
            ),
            interaction.Separator(),
            interaction.MediaGallery(
                [interaction.MediaGalleryItem(media, description="Gallery image")]
            ),
            interaction.File(interaction.UnfurledMediaItem("attachment://smoke.txt")),
        ],
        accent_color=0x5865F2,
    )
    return [
        container,
        interaction.ActionRow(
            [
                interaction.Button(
                    label="Open modal", custom_id="codex_smoke_modal", style=1
                ),
                interaction.Button(
                    label="Select modal", custom_id="codex_smoke_select_modal", style=2
                ),
            ]
        ),
        interaction.ActionRow([interaction.UserSelect("codex_smoke_user")]),
        interaction.ActionRow([interaction.RoleSelect("codex_smoke_role")]),
        interaction.ActionRow([interaction.MentionableSelect("codex_smoke_mention")]),
        interaction.ActionRow([interaction.ChannelSelect("codex_smoke_channel")]),
    ]


async def run(keep: bool, delete_id: int | None) -> None:
    load_local_env()
    token = required("DISCORD_TEST_BOT_TOKEN")
    application_id = int(required("DISCORD_TEST_APPLICATION_ID"))
    guild_id = int(required("DISCORD_GUILD_ID"))
    channel_id = int(required("DISCORD_TEST_CHANNEL_ID"))
    bot = interaction.Client(
        intents=discord.Intents.none(), application_id=application_id
    )
    message = None
    try:
        await bot.login(token)
        channel = await bot.fetch_channel(channel_id)
        if channel.guild.id != guild_id:
            raise ValueError("test channel is not in test guild")
        if delete_id is not None:
            original = await bot.http.get_message(channel_id, delete_id)
            if str(original["author"]["id"]) != str(bot.user.id):
                raise ValueError("refusing to delete another author's message")
            if "codex_smoke_modal" not in str(original.get("components", [])):
                raise ValueError("refusing to delete a non-smoke message")
            await bot.http.delete_message(channel_id, delete_id)
            print("smoke message deleted")
            return

        image_url = bot.user.display_avatar.url
        file = discord.File(
            BytesIO(b"Discord Components V2 live smoke test\n"), filename="smoke.txt"
        )
        message = await interaction.MessageTransferable(bot._connection, channel).send(
            components=message_components(image_url), file=file
        )
        data = await bot.http.get_message(channel_id, message.id)
        types = [item["type"] for item in data.get("components", [])]
        if not data.get("flags", 0) & 32768 or types != [17, 1, 1, 1, 1, 1]:
            raise AssertionError("Discord did not retain the V2 component layout")
        file_nodes = [
            child
            for top in data.get("components", [])
            for child in top.get("components", [])
            if child.get("type") == 13
        ]
        print(
            "file response:",
            [
                (
                    item.get("name"),
                    item.get("size"),
                    item.get("file", {}).get("url", "").split(":", 1)[0],
                )
                for item in file_nodes
            ],
            "attachments:",
            len(data.get("attachments", [])),
        )
        if not any(item.get("name") == "smoke.txt" for item in file_nodes):
            raise AssertionError("Discord did not retain the referenced attachment")
        print(
            "V2 container, thumbnail, gallery, file, button, four selects: REST round-trip passed"
        )
        if keep:
            print(
                f"message: https://discord.com/channels/{guild_id}/{channel_id}/{message.id}"
            )
            print(
                f"delete after visual check: examples/live_smoke_message.py --delete {message.id}"
            )
            message = None
        else:
            print("smoke message will be deleted")
    finally:
        if message is not None:
            await bot.http.delete_message(channel_id, message.id)
        await bot.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--keep", action="store_true", help="leave the message for visual inspection"
    )
    parser.add_argument(
        "--delete",
        type=int,
        metavar="MESSAGE_ID",
        help="remove a retained smoke message",
    )
    args = parser.parse_args()
    try:
        asyncio.run(run(args.keep, args.delete))
    except Exception as error:
        detail = str(error) if isinstance(error, (ValueError, AssertionError)) else ""
        print(
            f"smoke failed: {type(error).__name__} "
            f"(status={getattr(error, 'status', '-')}) {detail}"
        )
        raise SystemExit(1) from None
