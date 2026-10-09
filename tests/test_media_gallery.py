"""Media Gallery supports Discord's one-to-ten item structure."""

import pytest

from discord.ext import interaction


def test_media_gallery_round_trip_inside_container():
    media = interaction.UnfurledMediaItem("https://example.com/a.png")
    item = interaction.MediaGalleryItem(media, description="A", spoiler=True)
    gallery = interaction.MediaGallery([item], id=4)
    container = interaction.Container([gallery])
    restored = interaction.Container.from_payload(container.to_payload())
    assert restored.to_payload() == container.to_payload()
    assert isinstance(restored.components[0], interaction.MediaGallery)


@pytest.mark.parametrize("count", [0, 11])
def test_media_gallery_rejects_invalid_item_count(count):
    item = interaction.MediaGalleryItem(interaction.UnfurledMediaItem("https://example.com/a.png"))
    with pytest.raises(ValueError, match="1 to 10"):
        interaction.MediaGallery([item] * count)
