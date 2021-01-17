
from sources.imageurls import LAPROS_GRAPHIC_URL
from typing import Optional, Union
from discord.ext.commands.context import Context
from discord import Embed

def getLaprOSEmbed(title: str, description: str=None, fields: list[Union[tuple[str, str], tuple[str, str, bool]]]=None, imageURL: str=None):
    if not description: description = ""
    if not fields: fields = []
    
    e = Embed(
        title=title,
        description=description,
        color=0x00C0FF
    )
    for field in fields:
        e.add_field(
            name=field[0],
            value="\u200b" if not len(field) >= 2 else field[1],
            inline=False if not len(field) == 3 else field[2]
        )
    if imageURL:
        e.set_image(url=imageURL)
    e.set_thumbnail(url=LAPROS_GRAPHIC_URL)
    return e

async def dmError(ctx: Context, errorText: str):
    """ Sends a message to the author of a command that encountered an error. """
    await ctx.author.send(f"There was an error with your command `{ctx.message.content}` in the channel #{ctx.channel.name}:\n```\n{errorText}\n```")

def moderatorCheck(ctx: Context):
    
    return 550518609714348034 in [role.id for role in ctx.author.roles] or ctx.guild.id == 798023066718175252
