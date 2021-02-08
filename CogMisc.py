
from discordUtils import meCheck
from typing import Union
import discord
from discord.ext import commands
import random

import sources.text as T

M = T.MISC

class CogMisc(commands.Cog, **M.cog):
    def __init__(self):
        self.votes: dict[int, dict[str, list[int]]] = {}
    
    async def handleVoteAdd(self, reaction: discord.Reaction, user: Union[discord.Member, discord.User]):
        vote = self.votes.get(reaction.message.id)
        if not vote: return
        
        emoji = str(reaction.emoji)
        if not emoji in [M.emojiGreen, M.emojiRed]: await reaction.remove(user)
        
        oppositeReactors = vote[M.emojiGreen if emoji == M.emojiRed else M.emojiRed]
        if user.id in oppositeReactors:
            await reaction.remove(user)
        else:
            vote[emoji].append(user.id)
    
    async def handleVoteRemove(self, messageID: int, emoji: discord.PartialEmoji, userID: int):
        vote = self.votes.get(messageID)
        #print(vote)
        if not vote: return
        
        emoji = str(emoji)
        
        if emoji in [M.emojiGreen, M.emojiRed] and userID in vote[emoji]:
            vote[emoji].remove(userID)
    
    @commands.command(**M.vote.meta)
    async def vote(self, ctx: commands.Context):
        await ctx.message.add_reaction(M.emojiGreen)
        await ctx.message.add_reaction(M.emojiRed)
        self.votes[ctx.message.id] = {
            M.emojiGreen: [],
            M.emojiRed: []
        }
    
    @commands.command(**M.coinflip.meta)
    async def coinflip(self, ctx: commands.Context):
        """ Performs a coinflip, heads or tails. """
        await ctx.send(M.coinflip.heads if random.randint(0, 1) else M.coinflip.tails)
    
    @commands.command(**M.ping.meta, hidden=True)
    async def ping(self, ctx: commands.Context):
        await ctx.send(M.ping.pong)
    
    @commands.command(**M.cat.meta, hidden=True)
    @commands.check(meCheck)
    async def cat(self, ctx: commands.Context, *, here: str):
        await ctx.message.delete()
        await ctx.send(M.cat.cat(here))
    
    @commands.command(**M.sup.meta, hidden=True)
    async def sup(self, ctx: commands.Context):
        await ctx.send(M.sup.meta)
