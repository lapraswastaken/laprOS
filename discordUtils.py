
from discord.ext.commands.context import Context

async def dmError(ctx: Context, errorText: str):
    """ Sends a message to the author of a command that encountered an error. """
    await ctx.author.send(f"There was an error with your command `{ctx.message.content}` in the channel {ctx.channel.name} (<{ctx.message.jump_url}>):\n```md\n{errorText}\n```")
