
from Story import Story
from discord.ext.commands.context import Context
from discord import Embed
import json
from sources.imageurls import LAPROS_GRAPHIC_URL
from typing import Optional, Union

with open("./sources/archives.json", "r") as f:
    ARCHIVE_CHANNEL_IDS: dict[str, int] = {}
    loaded = json.loads(f.read())
    for channelIDstr in loaded:
        ARCHIVE_CHANNEL_IDS[int(channelIDstr)] = loaded[channelIDstr]


def getLaprOSEmbed(title: str, description: str=None, fields: list[Union[tuple[str, str], tuple[str, str, bool]]]=None, imageURL: str=None, footer=None, url=None):
    """ Creates a custom embed. """
    
    if not description: description = ""
    if not fields: fields = []
    
    e = Embed(
        title=title,
        description=description,
        color=0x00C0FF,
        url=url
    )
    for field in fields:
        e.add_field(
            name=field[0],
            value="\u200b" if not len(field) >= 2 else field[1],
            inline=False if not len(field) == 3 else field[2]
        )
    if imageURL:
        e.set_image(url=imageURL)
    if footer:
        e.set_footer(text=footer)
    e.set_thumbnail(url=LAPROS_GRAPHIC_URL)
    return e

async def dmError(ctx: Context, errorText: str):
    """ Sends a message to the author of a command that encountered an error. """
    
    await ctx.author.send(f"There was an error with your command `{ctx.message.content}` in the channel #{ctx.channel.name}:\n```\n{errorText}\n```")

def moderatorCheck(ctx: Context):
    """ Checks to see if the context's author is a moderator. """
    
    return 550518609714348034 in [role.id for role in ctx.author.roles] or ctx.guild.id == 798023066718175252
