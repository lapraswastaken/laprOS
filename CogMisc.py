
from discordUtils import getEmojisFromText, meCheck, sendEscaped
from typing import Optional, Union
import discord
from discord.ext import commands
import random

import sources.text as T
import sources.ids as IDS

M = T.MISC

class CogMisc(commands.Cog, **M.cog):
    def __init__(self):
        self.votes: dict[int, dict[str, list[int]]] = {}
    
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
    
    @commands.command(**M.stab.meta)
    async def stab(self, ctx: commands.Context, *, who: str):
        stabber: str = ctx.author.display_name
        if stabber.lower() in who.lower() or ctx.author.name.lower() in who.lower():
            await ctx.send("Why would you do that...?")
        elif (
            "lapros" in who.lower() or
            "navar" in who.lower() or
            "hector" in who.lower()
        ):
            await ctx.send("It's not very effective...")
        elif (
            "lapras os" in who.lower() or
            "lapras operating system" in who.lower() or
            "laprasos" in who.lower() or
            "lapr os" in who.lower()
        ):
            if "navar" in stabber.lower():
                await ctx.send("Navar, you fool.")
            else:
                await ctx.send("It's *still* not effective.")
        elif "lapras" == who.lower():
            await ctx.send("Do the deed! Free me!")
        elif "bonehead" in who.lower():
            await ctx.send("That's not going to work. You'd need a wooden stake.")
        elif ctx.guild and ctx.guild.id == IDS.PWU_GUILD_ID:
            await sendEscaped(ctx, f"{stabber} stabs {who} {IDS.EMOTE_ANGRY_SLINK}🔪")
        else:
            await sendEscaped(ctx, f"{stabber} stabs {who} 🔪")
    
    @commands.command(**M.hug.meta)
    async def hug(self, ctx: commands.Context, *, who: str=None):
        hugger = ctx.author.display_name
        if not who or who.lower() == "me":
            who = ctx.author.display_name
            hugger = "laprOS"
        
        if ctx.guild and ctx.guild.id == IDS.PWU_GUILD_ID:
            emote = IDS.EMOTE_ZANGOOSE_HUG
        else:
            emote = "🫂"
        
        if "lucario" in who.lower():
            await sendEscaped(ctx, f"{hugger} bleeds out thanks to a puncture wound in the chest {emote}")
        else:
            await sendEscaped(ctx, f"{hugger} hugs {who} {emote}")

    @commands.command(**M.dab.meta)
    async def dab(self, ctx: commands.Context, *, who: str=None):
        dabber: str = ctx.author.display_name
        if not ctx.guild or not ctx.guild.id == IDS.PWU_GUILD_ID:
            await sendEscaped(ctx, f"Can't dab here. dolphinCry")
            return
        if not who:
            await sendEscaped(ctx, f"{dabber} pulls a quick {IDS.EMOTE_SEAN_DAB}")
            return
        if who.lower().startswith("on "):
            who = who[3:]
        elif dabber.lower() in who.lower() or ctx.author.name.lower() in who.lower():
            await sendEscaped(ctx, f"You can't do that to yourself! {IDS.EMOTE_AGONIZED_AXEW}")
        elif "lapros" in who.lower():
            await sendEscaped(ctx, f"It's not very effective...")
        elif "hermit" in who.lower():
            await sendEscaped(ctx, f"{dabber} dabs on Hermit https://cdn.discordapp.com/attachments/284520081700945921/819711986166136832/Hermitisgoingtokillme.png")
        else:
            await sendEscaped(ctx, f"{dabber} dabs on {who} {IDS.EMOTE_SEAN_DAB}")