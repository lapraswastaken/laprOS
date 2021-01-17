
from Story import Story
import json
import random
from discordUtils import ARCHIVE_CHANNEL_IDS, getLaprOSEmbed, moderatorCheck
import discord
from discord.ext import commands
from StoryCog import ALL_GENRES, ALL_LINK_NAMES, ALL_RATINGS, StoryCog

with open("./sources/archiveguide.txt", "r") as f:
    TEXT_ARCHIVE_GUIDE = f.read()

class ArchiveCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @staticmethod
    def getStoryEmbed(story: Story, message: discord.Message):
        return getLaprOSEmbed(
            story.title,
            f"by {story.author.display_name}\n" + (f"```{story.summary}```" if story.summary else "") + "\n" + message.jump_url
        )
    
    @commands.command(hidden=True)
    async def emping(self, ctx: commands.Context):
        """ A test command for embeds. """
        await ctx.send(embed=getLaprOSEmbed(
            "Pong!",
            "`Hello, world!`"
        ))
    
    @commands.command(hidden=True)
    @commands.check(moderatorCheck)
    async def setarchivechannel(self, ctx: commands.Context, channel: discord.TextChannel):
        """ Sets the archive channel for this server. """
        ARCHIVE_CHANNEL_IDS[ctx.guild.id] = channel.id
        with open("./sources/archives.json", "w") as f:
            f.write(json.dumps(ARCHIVE_CHANNEL_IDS))

    @commands.command()
    async def archiveguide(self, ctx: commands.Context):
        """ Show a help message that explains how to add a story to the archive. """
        await ctx.send(embed=getLaprOSEmbed(
            "Archive guide",
            TEXT_ARCHIVE_GUIDE
        ))
    
    @commands.command()
    async def listgenres(self, ctx: commands.Context):
        """ Get a list of possible story genres to be added with `lap.addgenre`. """
        await ctx.send("List of all genres: ```\n" + "\n".join(ALL_GENRES) + "```\nIf your genre is not listed here, please let lapras (thebassethound) know.")
    
    @commands.command()
    async def listlinknames(self, ctx: commands.Context):
        """ Get a list of possible link names to be added with `lap.addlink`. """
        await ctx.send("List of all link names: ```\n" + "\n".join([f"{name} (used for {ALL_LINK_NAMES[name]})" for name in ALL_LINK_NAMES]) + "```\nIf your link name is not listed here, please let lapras (thebassethound) know.")
    
    @commands.command()
    async def listratings(self, ctx: commands.Context):
        """ Get a list of possible ratings to be set by `lap.setrating`. """
        await ctx.send("List of all ratings: ```\n" + "\n".join(ALL_RATINGS) + "```")
    
    @commands.command()
    async def randomstory(self, ctx: commands.Context):
        """ Get a random listing from the story archive. """
        archiveChannel = ctx.guild.get_channel(ARCHIVE_CHANNEL_IDS[ctx.guild.id])
        messages: list[discord.Message] = await archiveChannel.history().flatten()
        message = random.choice(messages)
        stories = await StoryCog.getStoriesFromMessage(message)
        story = random.choice(stories)
        await ctx.send(embed=ArchiveCog.getStoryEmbed(story, message))
            
