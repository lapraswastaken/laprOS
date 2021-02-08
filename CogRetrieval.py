
from typing import Union
import random

from discord.errors import NotFound
from discordUtils import fail, getLaprOSEmbed, moderatorCheck, paginate
import discord
from discord.ext import commands

from Archive import OVERARCH, Story
from CogArchive import CogArchive
import sources.text as T

R = T.RETR

class CogRetrieval(commands.Cog, **T.RETR.cog):
    
    @commands.command(**R.setArchiveChannel.meta, hidden=True)
    @commands.check(moderatorCheck)
    async def setArchiveChannel(self, ctx: commands.Context, channel: discord.TextChannel):
        
        OVERARCH.addArchive(ctx.guild.id, channel.id)
        OVERARCH.write()
        await ctx.send(R.setArchiveChannel.success)
    
    @commands.command(**R.setArchive.meta)
    async def setArchive(self, ctx: commands.Context):
        if not ctx.guild:
            fail(R.setArchive.errorDM)
        OVERARCH.setArchivePref(ctx.author.id, ctx.guild.id)
        OVERARCH.write()
        await ctx.send(R.setArchive.success(ctx.guild.name))
    
    @commands.command(**R.listGenres.meta)
    async def listGenres(self, ctx: commands.Context):
        await ctx.send(R.listGenres.success)
    
    @commands.command(**R.listSites.meta)
    async def listSites(self, ctx: commands.Context):
        await ctx.send(R.listSites.success)
    
    @commands.command(**R.listRatings.meta)
    async def listRatings(self, ctx: commands.Context):
        await ctx.send(R.listRatings.success)

    @commands.command(**R.archiveGuide.meta)
    async def archiveGuide(self, ctx: commands.Context):
        await paginate(ctx, [{"embed": getLaprOSEmbed(**page)} for page in R.archiveGuide.pages])
    
    @commands.command(**R.randomStory.meta)
    async def randomstory(self, ctx: commands.Context):
        archive = await CogArchive.getArchive(ctx)
        
        archiveChannel: discord.TextChannel = discord.utils.get(await ctx.guild.fetch_channels(), id=archive.channelID)
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
                await fail(R.randomStory.error)
        
        story = post.getRandomStory()
        await ctx.send(embed=getLaprOSEmbed(**R.randomStory.embed(story.title, author.display_name, story.summary, message.jump_url)))
    
    @commands.command(**R.searchByAuthor.meta)
    async def searchbyauthor(self, ctx: commands.Context, *, target: Union[discord.Member, int, str]):
        
        if isinstance(target, int):
            try:
                target: discord.Member = await ctx.guild.fetch_member(target)
            except NotFound:
                fail(R.searchByAuthor.errorID(target))
        if isinstance(target, str):
            def check(member: discord.Member):
                return member.display_name.startswith(target)
            found: discord.Member = discord.utils.find(check, ctx.guild.members)
            if not found:
                fail(R.searchByAuthor.errorName(target))
            target = found
        
        archive = await CogArchive.getArchive(ctx)
        archiveChannel: discord.TextChannel = discord.utils.get(await ctx.guild.fetch_channels(), id=archive.channelID)
        post = archive.getPost(target.id)
        if not post:
            fail(R.searchByAuthor.errorPost(target.display_name))
        message: discord.Message = await archiveChannel.fetch_message(post.messageID)
        
        await ctx.send(embed=getLaprOSEmbed(R.searchByAuthor.embed (target.display_name, message.jump_url)))
