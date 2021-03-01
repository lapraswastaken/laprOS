
from typing import Union
import random

from discord.errors import NotFound
from discordUtils import canHandleArchive, convertMember, fail, fetchChannel, getGuildFromContext, getLaprOSEmbed, isModerator, moderatorCheck, paginate
import discord
from discord.ext import commands

from Archive import NotFoundException, OVERARCH, Story
from CogArchive import CogArchive, getArchiveFromContext, getAuthorFromContext
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
        author = await getAuthorFromContext(ctx)
        OVERARCH.setArchivePref(author.id, ctx.guild.id)
        OVERARCH.write()
        await ctx.send(R.useHere.success(ctx.guild.name))
    
    @commands.command(**R.proxy.meta, hidden=True)
    async def proxy(self, ctx: commands.Context, *, member: Union[discord.Member, int]):
        if not isModerator(ctx.author):
            fail(T.UTIL.errorNotMod)
        member = await convertMember(member, ctx)
        if member.id == ctx.author.id:
            fail(R.proxy.selfProxy)
        OVERARCH.setProxy(ctx.author.id, member.id)
        
        messageable = ctx.author if canHandleArchive(ctx) else ctx

        await messageable.send(R.proxy.success(member.display_name))
            
    @commands.command(**R.getProxy.meta, hidden=True)
    async def getProxy(self, ctx: commands.Context):
        author = await getAuthorFromContext(ctx)
        if author.id == ctx.author.id:
            await ctx.send(R.noProxy)
        else:
            await ctx.send(R.getProxy.proxy(author.display_name))
    
    @commands.command(**R.clearProxy.meta, hidden=True)
    async def clearProxy(self, ctx: commands.Context):
        proxiedUser = await getAuthorFromContext(ctx)
        try:
            OVERARCH.clearProxy(ctx.author.id)
        except NotFoundException:
            fail(R.noProxy)
        await ctx.send(R.clearProxy.success(proxiedUser.display_name))
    
    @commands.command(**R.dmMe.meta)
    async def dmMe(self, ctx: commands.Context):
        await ctx.author.send(R.dmMe.success)
    
    @commands.command(**R.whichArchive.meta)
    async def whichArchive(self, ctx: commands.Context):
        author = await getAuthorFromContext(ctx)
        guildID = OVERARCH.getGuildIDForUser(author.id)
        if not guildID:
            fail(T.UTIL.errorNoArchivePreference)
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
    
    @commands.group(**R.fetch.meta, pass_context=True, invoke_without_command=True)
    async def fetch(self, ctx: commands.Context, *args: str):
        if not args:
            fail(R.fetch.noArgs)
        if not ctx.invoked_subcommand:
            fail(R.fetch.error(" ".join(args)))
    
    @fetch.command(**R.byRandom.meta)
    async def byRandom(self, ctx: commands.Context):
        archive = getArchiveFromContext(ctx)
        
        archiveChannel: discord.TextChannel = await fetchChannel(ctx.guild, archive.channelID)
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
                await fail(R.byRandom.error)
        
        story = post.getRandomStory()
        await ctx.send(embed=getLaprOSEmbed(**R.byRandom.embed(story.title, author.display_name, story.summary, message.jump_url)))
    
    @fetch.command(**R.byAuthor.meta, pass_context=True)
    async def byAuthor(self, ctx: commands.Context, *, author: Union[discord.Member, int]):
        author = await convertMember(author, ctx)
        archive = getArchiveFromContext(ctx)
        archiveChannel: discord.TextChannel = await fetchChannel(ctx.guild, archive.channelID)
        
        post = archive.getPost(author.id)
        try:
            message: discord.Message = await archiveChannel.fetch_message(post.messageID)
        except NotFound:
            fail(R.byAuthor.noPost(author))
        await ctx.send(embed=getLaprOSEmbed(**R.byAuthor.embed(author.display_name, post.getStoryTitles(), message.jump_url)))
