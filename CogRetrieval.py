
from typing import Union
import random
from discordUtils import getLaprOSEmbed, moderatorCheck
import discord
from discord.ext import commands

from Archive import OVERARCH, Story
from CogArchive import CogArchive
import sources.text as T

class CogRetrieval(
    commands.Cog,
    name=T.RETR.cogName,
    description=T.RETR.cogDescription):
    
    @staticmethod
    def getStoryEmbed(story: Story, author: discord.Member, message: discord.Message):
        """ Formats and returns an embed with the custom logo, displaying a story's title, its author, its summary, and the message it belongs to. """
        
        return getLaprOSEmbed(
            T.RETR.embedStoryTitle(story.title),
            T.RETR.embedStoryDescription(author.display_name, story.summary, message.jump_url)
        )
    
    @commands.command(**T.RETR.cmd.setArchiveChannel, hidden=True)
    @commands.check(moderatorCheck)
    async def setArchiveChannel(self, ctx: commands.Context, channel: discord.TextChannel):
        
        OVERARCH.addArchive(ctx.guild.id, channel.id)
        OVERARCH.write()

    @commands.command(**T.RETR.cmd.archiveGuide)
    async def archiveGuide(self, ctx: commands.Context):
        
        await ctx.send(embed=getLaprOSEmbed(
            T.RETR.embedGuideTitle,
            T.RETR.embedGuideDescription
        ))
    
    @commands.command(**T.RETR.cmd.listGenres)
    async def listGenres(self, ctx: commands.Context):
        await ctx.send(T.RETR.listGenre)
    
    @commands.command(**T.RETR.cmd.listSites)
    async def listSites(self, ctx: commands.Context):
        await ctx.send(T.RETR.listSiteAbbrs)
    
    @commands.command(**T.RETR.cmd.listRatings)
    async def listRatings(self, ctx: commands.Context):
        """ Get a list of possible ratings to be set by `lap.setrating`. """
        
        await ctx.send(T.RETR.listRatings)
    
    @commands.command(**T.RETR.cmd.randomStory)
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
                await ctx.send(T.RETR.errorRandomStoryFail)
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
            T.RETR.embedSearchAuthorTitle(target.display_name),
            T.RETR.embedSearchAuthorDescription(None if not message else message.jump_url)
        ))
