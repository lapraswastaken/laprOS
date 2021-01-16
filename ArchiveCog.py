
from discordUtils import getLaprOSEmbed
from discord.ext.commands.bot import Bot
from discord.ext.commands.cog import Cog
from discord.ext.commands.context import Context
from discord.ext.commands.core import command
from StoryCog import ALL_LINK_NAMES, ALL_RATINGS, StoryCog, ALL_GENRES

with open("./sources/archiveguide.txt", "r") as f:
    TEXT_ARCHIVE_GUIDE = f.read()

class ArchiveCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
    
    @command()
    async def emping(self, ctx: Context):
        await ctx.send(embed=getLaprOSEmbed(
            "Pong!",
            "`Hello, world!`"
        ))

    @command()
    async def archiveguide(self, ctx: Context):
        await ctx.send(embed=getLaprOSEmbed(
            "Archive guide",
            TEXT_ARCHIVE_GUIDE
        ))
    
    @command()
    async def listgenres(self, ctx: Context):
        await ctx.send("List of all genres: ```" + "\n".join(ALL_GENRES) + "```")
    
    @command()
    async def listlinknames(self, ctx: Context):
        await ctx.send("List of all link names: ```" + "\n".join(ALL_LINK_NAMES) + "```")
    
    @command()
    async def listratings(self, ctx: Context):
        await ctx.send("List of all ratings: ```" + "\n".join(ALL_RATINGS) + "```")
