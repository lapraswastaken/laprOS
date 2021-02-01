
from Archive import OVERARCH
from typing import Union
from Story import Story
import random
from discordUtils import getLaprOSEmbed, moderatorCheck
import discord
from discord.ext import commands
import sources.textArchive as T_ARCH
import sources.textRetrieval as T_RETR
from CogArchive import CogArchive

class CogRetrieval(
    commands.Cog,
    name=T_RETR.cogName,
    description=T_RETR.cogDescription):
    
    @staticmethod
    def getStoryEmbed(story: Story, author: discord.Member, message: discord.Message):
        return getLaprOSEmbed(
            T_RETR.embedStoryTitle(story.title),
            T_RETR.embedStoryDescription(author.display_name, story.summary, message.jump_url)
        )
    
    @commands.command(name=T_RETR.cmdSetArchiveChannel, help=T_RETR.cmdSetArchiveChannelHelp, hidden=True)
    @commands.check(moderatorCheck)
    async def setarchivechannel(self, ctx: commands.Context, channel: discord.TextChannel):
        """ Sets the archive channel for this server. """
        
        OVERARCH.addArchive(ctx.guild.id, channel.id)
        OVERARCH.write()

    @commands.command()
    async def archiveguide(self, ctx: commands.Context):
        """ Show a help message that explains how to add a story to the archive. """
        
        await ctx.send(embed=getLaprOSEmbed(
            T_RETR.embedGuideTitle,
            T_RETR.embedGuideDescription
        ))
    
    @commands.command()
    async def listgenres(self, ctx: commands.Context):
        """ Get a list of possible story genres to be added with `addgenre`. """
        
        await ctx.send(T_RETR.listGenre)
    
    @commands.command()
    async def listsites(self, ctx: commands.Context):
        """ Get a list of possible site abbreviations to be added with `addlink`. """
        
        await ctx.send(T_RETR.listSiteAbbrs)
    
    @commands.command()
    async def listratings(self, ctx: commands.Context):
        """ Get a list of possible ratings to be set by `lap.setrating`. """
        
        await ctx.send(T_RETR.listRatings)
    
    @commands.command()
    async def randomstory(self, ctx: commands.Context):
        """ Get a random listing from the story archive. """
        
        archive = await CogArchive.getArchive(ctx)
        
        archiveChannel: discord.TextChannel = ctx.guild.get_channel(archive.channelID)
        post = archive.getRandomPost()
        attempts = 100
        while True:
            try:
                message: discord.Message = await archiveChannel.fetch_message(post.messageID)
        
                author: discord.Member = await ctx.guild.fetch_member(post.authorID)
                if not author: raise discord.DiscordException()
                break
            except discord.DiscordException:
                post = archive.getRandomPost()
                
            attempts -= 1
            if attempts <= 0:
                await ctx.send(T_RETR.errorRandomStoryFail)
                return
        
        story = post.getRandomStory()
        await ctx.send(embed=CogRetrieval.getStoryEmbed(story, author, message))
    
    @commands.command()
    async def searchbyauthor(self, ctx: commands.Context, target: Union[discord.Member, int]):
        """ Get a link to the archive post for a given user. The argument can be the mention of a user or the user's ID. """
        
        if isinstance(target, int):
            target: discord.Member = await ctx.guild.fetch_member(target)
        
        archive = await CogArchive.getArchive(ctx)
        archiveChannel: discord.TextChannel = await ctx.guild.get_channel(archive.channelID)
        post = archive.getPost(target.id)
        message: discord.Message = await archiveChannel.fetch_message(post.messageID)
        
        await ctx.send(embed=getLaprOSEmbed(
            T_RETR.embedSearchAuthorTitle(target.display_name),
            T_RETR.embedSearchAuthorDescription(None if not message else message.jump_url)
        ))
