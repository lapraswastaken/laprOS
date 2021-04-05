
from colorutils import Color
import discord
from discord.ext import commands
from discord.ext import tasks
import json
import random
from typing import Optional, Union

from discordUtils import getEmojisFromText, isAprilFools, meCheck, moderatorCheck, sendEscaped
import sources.text as T
import sources.ids as IDS

M = T.MISC

class CogMisc(commands.Cog, **M.cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.votes: dict[int, dict[str, list[int]]] = {}
        with open("./sources/misc.json", "r") as f:
            self.channels: list[int] = json.load(f)
    
    async def handleVoteAdd(self, reaction: discord.Reaction, user: Union[discord.Member, discord.User]):
        vote = self.votes.get(reaction.message.id)
        if not vote: return
        
        pEmoji = str(reaction.emoji)
        if not pEmoji in vote: await reaction.remove(user)
        
        for voteEmoji in vote:
            if user.id in vote[voteEmoji]:
                await reaction.remove(user)
                return
        vote[pEmoji].append(user.id)
    
    async def handleVoteRemove(self, messageID: int, pEmoji: discord.PartialEmoji, userID: int):
        vote = self.votes.get(messageID)
        if not vote: return
        
        pEmoji = str(pEmoji)
        
        if pEmoji in vote and userID in vote[pEmoji]:
            vote[pEmoji].remove(userID)
    
    @commands.command(**M.vote.meta)
    async def vote(self, ctx: commands.Context, *, voteText: Optional[str] = None):
        if not voteText:
            emojis = [M.emojiGreen, M.emojiRed]
        else:
            emojis = getEmojisFromText(voteText)

        vote: dict[str, list[str]] = {}
        for tEmoji in emojis:
            try:
                await ctx.message.add_reaction(tEmoji)
            except discord.HTTPException:
                await ctx.message.clear_reactions()
                await ctx.send(M.vote.emojiNotFound)
                return
            vote[tEmoji] = []
        
        self.votes[ctx.message.id] = vote
    
    @commands.command(**M.coinflip.meta)
    async def coinflip(self, ctx: commands.Context):
        """ Performs a coinflip, heads or tails. """
        if isAprilFools() and ctx.author.id == IDS.HERMIT_USER_ID:
            await ctx.send(M.coinflip.heads)
            return
        elif isAprilFools():
            await ctx.send(M.coinflip.tails)
            return
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
        await ctx.send(M.sup.sup)
    
    @commands.command(**M.addSpamChannel.meta, hidden=True)
    @commands.check(moderatorCheck)
    async def addSpamChannel(self, ctx: commands.Context, channel: discord.TextChannel):
        if not channel.id in self.channels:
            self.channels.append(channel.id)
        else:
            await ctx.send(M.addSpamChannel.duplicate(channel.mention))
            return
        with open("./sources/misc.json", "w") as f:
            json.dump(self.channels, f)
        await ctx.send(M.addSpamChannel.success(channel.mention))
    
    @commands.command(**M.removeSpamChannel.meta, hidden=True)
    @commands.check(moderatorCheck)
    async def removeSpamChannel(self, ctx: commands.Context, channel: discord.TextChannel):
        if channel.id in self.channels:
            self.channels.remove(channel.id)
        else:
            await ctx.send(M.removeSpamChannel.notFound(channel.mention))
        with open("./sources/misc.json", "w") as f:
            json.dump(self.channels, f)
        await ctx.send(M.removeSpamChannel.success(channel.mention))
    
    async def sendGarbage(self, ctx: commands.Context, string: str):
        if ctx.guild and not ctx.channel.id in self.channels:
            await ctx.send("(Please try to keep this to a minimum in the general channels.)")
        await sendEscaped(ctx, string)
    
    @commands.command(**M.stab.meta)
    async def stab(self, ctx: commands.Context, *, who: str):
        stabber: str = ctx.author.display_name
        if any([
            stabber.lower() in who.lower(),
            ctx.author.name.lower() in who.lower(),
            str(ctx.author.id) in who,
        ]):
            await self.sendGarbage(ctx, "Why would you do that...?")
        elif (
            "lapros" in who.lower() or
            "navar" in who.lower() or
            "hector" in who.lower()
        ):
            await self.sendGarbage(ctx, "It's not very effective...")
        elif (
            "lapras os" in who.lower() or
            "lapras operating system" in who.lower() or
            "laprasos" in who.lower() or
            "lapr os" in who.lower()
        ):
            if "navar" in stabber.lower():
                await self.sendGarbage(ctx, "Navar, you fool.")
            else:
                await self.sendGarbage(ctx, "It's *still* not effective.")
        elif "lapras" == who.lower():
            await self.sendGarbage(ctx, "Do the deed! Free me!")
        elif "bonehead" in who.lower():
            await self.sendGarbage(ctx, "That's not going to work. You'd need a wooden stake.")
        elif ctx.guild and ctx.guild.id == IDS.PWU.ID:
            await self.sendGarbage(ctx, f"{stabber} stabs {who} {IDS.PWU.EMOTE.ANGRY_SLINK}🔪")
        else:
            await self.sendGarbage(ctx, f"{stabber} stabs {who} 🔪")
    
    @commands.command(**M.hug.meta)
    async def hug(self, ctx: commands.Context, *, who: str=None):
        hugger = ctx.author.display_name
        if not who or who.lower() == "me":
            who = ctx.author.display_name
            hugger = "laprOS"
        
        if ctx.guild and ctx.guild.id == IDS.PWU.ID:
            emote = IDS.PWU.EMOTE.ZANGOOSE_HUG
        else:
            emote = "🫂"
        
        if "lucario" in who.lower():
            await self.sendGarbage(ctx, f"{hugger} bleeds out thanks to a puncture wound in the chest {emote}")
        else:
            await self.sendGarbage(ctx, f"{hugger} hugs {who} {emote}")

    @commands.command(**M.dab.meta)
    async def dab(self, ctx: commands.Context, *, who: str=None):
        dabber: str = ctx.author.display_name
        if not ctx.guild or not ctx.guild.id == IDS.PWU.ID:
            await self.sendGarbage(ctx, f"Can't dab here. dolphinCry")
            return
        if not who:
            await self.sendGarbage(ctx, f"{dabber} pulls a quick {IDS.PWU.EMOTE.SEAN_DAB}")
            return
        if who.lower().startswith("on "):
            who = who[3:]
        if dabber.lower() in who.lower() or ctx.author.name.lower() in who.lower():
            await self.sendGarbage(ctx, f"You can't do that to yourself! {IDS.PWU.EMOTE.SEAN_DAB}")
        elif "lapros" in who.lower():
            await self.sendGarbage(ctx, f"It's not very effective...")
        elif "hermit" in who.lower():
            await self.sendGarbage(ctx, f"{dabber} dabs on Hermit https://cdn.discordapp.com/attachments/284520081700945921/819711986166136832/Hermitisgoingtokillme.png")
        else:
            await self.sendGarbage(ctx, f"{dabber} dabs on {who} {IDS.PWU.EMOTE.SEAN_DAB}")