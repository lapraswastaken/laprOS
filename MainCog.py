
from typing import Optional, Union
from discord.partial_emoji import PartialEmoji
from discord.user import User
from discord.ext.commands import Cog, command
from discord.ext.commands.context import Context
from discord.member import Member
from discord.reaction import Reaction

class MainCog(Cog):
    def __init__(self, bot):
        self.bot = bot
        
        self.votes: dict[int, dict[str, list[int]]] = {}
    
    async def handleVoteAdd(self, reaction: Reaction, user: Union[Member, User]):
        vote = self.votes.get(reaction.message.id)
        if not vote: return
        
        emoji = str(reaction.emoji)
        if not emoji in ["🟢", "🔴"]: await reaction.remove(user)
        
        oppositeReactors = vote["🟢" if emoji == "🔴" else "🔴"]
        if user.id in oppositeReactors:
            await reaction.remove(user)
        else:
            vote[emoji].append(user.id)
    
    async def handleVoteRemove(self, messageID: int, emoji: PartialEmoji, userID: int):
        vote = self.votes.get(messageID)
        #print(vote)
        if not vote: return
        
        emoji = str(emoji)
        
        if emoji in ["🟢", "🔴"] and userID in vote[emoji]:
            vote[emoji].remove(userID)
    
    @command()
    async def ping(self, ctx: Context):
        await ctx.send("Pong")
    
    @command()
    async def vote(self, ctx: Context):
        """ Starts a vote on the command's message. """
        await ctx.message.add_reaction("🟢")
        await ctx.message.add_reaction("🔴")
        self.votes[ctx.message.id] = {
            "🟢": [],
            "🔴": []
        }
    
    #@command()
    #async def pog(self, ctx: Context):
    #    if ctx.guild.id == 546872429621018635:
    #        pass
    
    @command(hidden=True)
    async def engineer(self, ctx: Context, gaming: str=None):
        if not gaming == "gaming":
            await ctx.send("Engineer *what now?*")
        else:
            await ctx.send("engineer gaming")
