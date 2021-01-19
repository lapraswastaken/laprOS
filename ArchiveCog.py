
from Archive import OVERARCH
from typing import Union
from Story import Story
import json
import random
from discordUtils import getLaprOSEmbed, moderatorCheck
import discord
from discord.ext import commands
from StoryCog import ALL_GENRES, ALL_LINK_NAMES, ALL_RATINGS, StoryCog

with open("./sources/archiveguide.txt", "r") as f:
    TEXT_ARCHIVE_GUIDE = f.read()

class ArchiveCog(commands.Cog):
    
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
        
        OVERARCH.addArchive(ctx.guild.id, channel.id)
        OVERARCH.write()

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
        
        archiveChannel = getArchiveChannelForContext(ctx)
        messages = StoryCog.getMessagesFromChannel(archiveChannel)
        message = random.choice(messages)
        stories = await StoryCog.getStoriesFromMessage(message)
        story = random.choice(stories)
        await ctx.send(embed=ArchiveCog.getStoryEmbed(story, message))
    
    @commands.command()
    async def searchbyauthor(self, ctx: commands.Context, target: Union[discord.Member, int]):
        """ Get a link to the archive post for a given user. The argument can be the mention of a user or the user's ID. """
        
        if isinstance(target, int):
            target = await ctx.guild.fetch_member(target)
        
        archiveChannel = getArchiveChannelForContext(ctx)
        message = await StoryCog.getMessageForAuthor(archiveChannel, target)
            
        await ctx.send(embed=getLaprOSEmbed(
            f"Stories by {target.display_name}",
            f"Archive post:\n{message.jump_url}" if message else f"{target.display_name} doesn't have any posts in the story archive."
        ))
    
    @commands.command()
    async def searchbygenre(self, ctx: commands.Context, targetGenre: str):
        """ Get a list of links to archive posts containing stories with the given genre. """
        if not targetGenre in ALL_GENRES:
            await ctx.send(f"{targetGenre} is not a valid genre.")
            return
        archiveChannel = getArchiveChannelForContext(ctx)
        messages = await StoryCog.getMessagesFromChannel(archiveChannel)
        storiesAndMessages: list[tuple[Story, discord.Message]] = []
        for message in messages:
            toAdd = await StoryCog.getStoriesFromMessage(message)
            for story in toAdd:
                if targetGenre in story.genres:
                    storiesAndMessages.append((story, message))
        if storiesAndMessages:
            await ctx.send(embed=getLaprOSEmbed(
                f"{targetGenre} stories",
                fields=[(storyAndMessage[0].title, storyAndMessage[1].jump_url) for storyAndMessage in storiesAndMessages]
            ))
