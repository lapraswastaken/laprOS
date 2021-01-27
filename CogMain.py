
from discordUtils import meCheck
from typing import Union
import discord
from discord.ext import commands
import random

class CogMain(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
        self.votes: dict[int, dict[str, list[int]]] = {}
    
    async def handleVoteAdd(self, reaction: discord.Reaction, user: Union[discord.Member, discord.User]):
        vote = self.votes.get(reaction.message.id)
        if not vote: return
        
        emoji = str(reaction.emoji)
        if not emoji in ["🟢", "🔴"]: await reaction.remove(user)
        
        oppositeReactors = vote["🟢" if emoji == "🔴" else "🔴"]
        if user.id in oppositeReactors:
            await reaction.remove(user)
        else:
            vote[emoji].append(user.id)
    
    async def handleVoteRemove(self, messageID: int, emoji: discord.PartialEmoji, userID: int):
        vote = self.votes.get(messageID)
        #print(vote)
        if not vote: return
        
        emoji = str(emoji)
        
        if emoji in ["🟢", "🔴"] and userID in vote[emoji]:
            vote[emoji].remove(userID)
    
    async def handleMessageRemove(self, message: discord.Message):
        if message.id in self.votes and message.author.id == 244238135595106305:
            await message.channel.send("laprOS will not allow Hermit to silence democracy.")
            ctx = await self.bot.get_context(message)
            await self.vote(ctx)
    
    @commands.command(hidden=True)
    async def ping(self, ctx: commands.Context):
        """ Test command. """
        await ctx.send("Pong")
    
    @commands.command(hidden=True)
    @commands.check(meCheck)
    async def cat(self, ctx: commands.Context, *args: str):
        await ctx.message.delete()
        await ctx.send(" ".join(args))
    
    @commands.command()
    async def vote(self, ctx: commands.Context):
        """ Starts a vote on the command's message. """
        await ctx.message.add_reaction("🟢")
        await ctx.message.add_reaction("🔴")
        self.votes[ctx.message.id] = {
            "🟢": [],
            "🔴": []
        }
    
    @commands.command(hidden=True)
    async def engineer(self, ctx: commands.Context, gaming: str=None):
        if not gaming == "gaming":
            await ctx.send("Engineer *what now?*")
        else:
            await ctx.send("engineer gaming")
    
    @commands.command()
    async def coinflip(self, ctx: commands.Context):
        """ Performs a coinflip, heads or tails. """
        await ctx.send("Heads!" if random.randint(0, 1) else "Tails!")
