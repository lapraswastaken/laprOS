
import discord
from Story import Story
from discord.ext import commands
from discord import Embed
import sources.general as T_GEN
import sources.textErrors as T_ERR
import sources.ids as IDS
from typing import Optional, Union


def getEmbed(title: str, description: str=None, fields: list[Union[tuple[str, str], tuple[str, str, bool]]]=None, imageURL: str=None, footer=None, url=None):
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
            value=T_GEN.empty if not len(field) >= 2 else field[1],
            inline=False if not len(field) == 3 else field[2]
        )
    if imageURL:
        e.set_image(url=imageURL)
    if footer:
        e.set_footer(text=footer)
    return e

def getLaprOSEmbed(title: str, description: str=None, fields: list[Union[tuple[str, str], tuple[str, str, bool]]]=None, imageURL: str=None, footer=None, url=None):
    e = getEmbed(title, description, fields, imageURL, footer, url)
    e.set_thumbnail(url=T_GEN.LAPROS_GRAPHIC_URL)
    return e

async def dmError(ctx: commands.Context, errorText: str):
    """ Sends a message to the author of a command that encountered an error. """
    if isinstance(ctx.channel, discord.DMChannel):
        await ctx.author.send(T_ERR.dmMessage(errorText))
    else:
        await ctx.author.send(T_ERR.dmMessageWithChannel(ctx.message.content[:1500], ctx.channel.id, errorText))

def checkIsBotID(id: int):
    return id in IDS.botIDs
    
def meCheck(ctx: commands.Context):
    return ctx.author.id == IDS.myID

def moderatorCheck(ctx: commands.Context):
    """ Checks to see if the context's author is a moderator. """
    
    return 550518609714348034 in [role.id for role in ctx.author.roles] or ctx.guild.id == 798023066718175252
