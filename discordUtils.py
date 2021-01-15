
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
    e.set_thumbnail(url="https://cdn.discordapp.com/attachments/284520081700945921/799416249738067978/laprOS_logo.png")
    return e

async def dmError(ctx: Context, errorText: str):
    """ Sends a message to the author of a command that encountered an error. """
    await ctx.author.send(f"There was an error with your command `{ctx.message.content}` in the channel {ctx.channel.name} (<{ctx.message.jump_url}>):\n```md\n{errorText}\n```")
