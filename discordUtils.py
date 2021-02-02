
import discord
from Story import Story
from discord.ext import commands
from discord import Embed
from sources.general import LAPROS_GRAPHIC_URL, EMPTY
from sources.ids import BOT_USER_IDS, MY_USER_ID
import sources.text as T
from typing import Union


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
            value=EMPTY if not len(field) >= 2 else field[1],
            inline=False if not len(field) == 3 else field[2]
        )
    if imageURL:
        e.set_image(url=imageURL)
    if footer:
        e.set_footer(text=footer)
    return e

def getLaprOSEmbed(title: str, description: str=None, fields: list[Union[tuple[str, str], tuple[str, str, bool]]]=None, imageURL: str=None, footer=None, url=None):
    e = getEmbed(title, description, fields, imageURL, footer, url)
    e.set_thumbnail(url=LAPROS_GRAPHIC_URL)
    return e

async def dmError(ctx: commands.Context, errorText: str):
    """ Sends a message to the author of a command that encountered an error. """
    if isinstance(ctx.channel, discord.DMChannel):
        await ctx.author.send(T.ERR.dmMessage(errorText))
    else:
        await ctx.author.send(T.ERR.dmMessageWithChannel(ctx.message.content[:1500], ctx.channel.id, errorText))
    
async def dmErrorAndRaise(ctx: commands.Context, errorText: str) -> Exception:
    """ Sends a message to the author of a command that encountered an error, then raises a commands.CheckFailure. """
    await dmError(ctx, errorText)
    raise commands.CheckFailure()

def checkIsBotID(id: int):
    return id in BOT_USER_IDS
    
def meCheck(ctx: commands.Context):
    return ctx.author.id == MY_USER_ID

def moderatorCheck(ctx: commands.Context):
    """ Checks to see if the context's author is a moderator. """
    
    return 550518609714348034 in [role.id for role in ctx.author.roles] or ctx.guild.id == 798023066718175252

def getStringArgsFromText(text: str):
    
    args: list[str] = []
    inQuote = False
    for word in text.split(" "):
        if word.startswith("\"") and not inQuote and not len(word) == 1:
            word = word[1:]
            args.append("")
            inQuote = True
        
        if inQuote:
            if word.endswith("\""):
                word = word[:-1]
                inQuote = False
            
            args[-1] = (args[-1] + f" {word}").strip()
        else:
            args.append(word)
    if inQuote:
        raise SyntaxError("Encountered end of line when parsing string")
    return args
