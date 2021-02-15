
from typing import Union
import random

from discord.errors import NotFound
from discordUtils import fail, fetchChannel, getLaprOSEmbed, moderatorCheck, paginate
import discord
from discord.ext import commands

from Archive import NotFoundException, OVERARCH, Story
from CogArchive import CogArchive, getArchiveFromContext
import sources.text as T

R = T.RETR

class CogRetrieval(commands.Cog, **T.RETR.cog):
    def __init__(self, bot: commands.Bot, cogArchive: CogArchive):
        self.bot = bot
        self.cogArchive = cogArchive
    
    @commands.command(**R.setArchiveChannel.meta, hidden=True)
    @commands.check(moderatorCheck)
    async def setArchiveChannel(self, ctx: commands.Context, channel: discord.TextChannel):
        
        OVERARCH.addArchive(ctx.guild.id, channel.id)
        OVERARCH.write()
        await ctx.send(R.setArchiveChannel.success)
    
    @commands.command(**R.useHere.meta)
    async def useHere(self, ctx: commands.Context):
        if not ctx.guild:
            fail(R.useHere.errorDM)
        author = await self.cogArchive.checkIsUserProxied(ctx.author)
        OVERARCH.setArchivePref(author.id, ctx.guild.id)
        OVERARCH.write()
        await ctx.send(R.useHere.success(ctx.guild.name))
    
    @commands.command(**R.proxyUser.meta, ignore_extra=False, hidden=True)
    @commands.check(moderatorCheck)
    async def proxyUser(self, ctx: commands.Context, member: Union[discord.Member, int]):
        if isinstance(ctx.channel, discord.DMChannel):
            # this condition will never be met because of the moderatorCheck?
            fail(R.proxyUser.errorDM)
        if isinstance(member, int):
            member = await ctx.guild.get_member(member)
        self.cogArchive.proxies[ctx.author.id] = member
        await ctx.author.send(R.proxyUser.success(member.display_name))
            
    @commands.command(**R.getProxy.meta)
    async def getProxy(self, ctx: commands.Context):
        author = await self.cogArchive.checkIsUserProxied(ctx.author)
        if author.id == ctx.author.id:
            await ctx.send(R.getProxy.noProxy)
        else:
            await ctx.send(R.getProxy.proxy(author.display_name))
    
    @commands.command(**R.clearProxy.meta, ignore_extra=False, hidden=True)
    async def clearProxy(self, ctx: commands.Context):
        if ctx.author.id in self.cogArchive.proxies:
            proxy = await self.cogArchive.checkIsUserProxied(ctx.author)
            await ctx.author.send(R.clearProxy.success(proxy.display_name))
        else:
            fail(ctx, R.clearProxy.noProxy)
    
    @commands.command(**R.whichArchive.meta)
    async def whichArchive(self, ctx: commands.Context):
        author = await self.cogArchive.checkIsUserProxied(ctx.author)
        guildID = OVERARCH.getGuildIDForUser(author.id)
        if not guildID:
            fail(R.errorNoArchivePreference)
        guild: discord.Guild = await self.bot.fetch_guild(guildID)
        await ctx.send(R.whichArchive.success(guild.name))
    
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
        try:
            archive = getArchiveFromContext(ctx.author.id)
        except NotFoundException:
            fail(R.errorNoArchivePreference)
        
        archiveChannel: discord.TextChannel = fetchChannel(ctx.guild, archive.guildID)
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
