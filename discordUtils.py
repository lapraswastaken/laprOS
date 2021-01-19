
import discord
from Story import Story
from discord.ext import commands
from discord import Embed
import json
from typing import Optional, Union

LAPROS_GRAPHIC_URL = "https://cdn.discordapp.com/attachments/284520081700945921/799416249738067978/laprOS_logo.png"
BOT_IDS = [768554429305061387, 785222129061986304]

def checkIsBotID(id: int):
    return id in BOT_IDS

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

async def dmError(ctx: commands.Context, errorText: str):
    """ Sends a message to the author of a command that encountered an error. """
    if isinstance(ctx.channel, discord.DMChannel):
        await ctx.author.send(f"There was an error with your command:\n```\n{errorText}\n```")
    else:
        await ctx.author.send(f"There was an error with your command `{ctx.message.content}` in the channel #{ctx.channel.name}:\n```\n{errorText}\n```")

def moderatorCheck(ctx: commands.Context):
    """ Checks to see if the context's author is a moderator. """
    
    return 550518609714348034 in [role.id for role in ctx.author.roles] or ctx.guild.id == 798023066718175252
