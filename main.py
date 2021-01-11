
from StoryCog import StoryCog
from typing import Union
from discord.ext.commands import Bot
from discord.ext.commands.context import Context
from discord.member import Member
from discord.reaction import Reaction
from discord.user import User
import os
from MainCog import MainCog

storyLinksChannelIDs = [794355705368018954, 792629600860897330, 798023111453966347]

bot = Bot(command_prefix=".")
mainCog = MainCog(bot)
bot.add_cog(mainCog)
bot.add_cog(StoryCog(bot, storyLinksChannelIDs))

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}.")

@bot.event
async def on_reaction_add(reaction: Reaction, user: Union[User, Member]):
    await mainCog.handleVoteAdd(reaction, user)

@bot.event
async def on_reaction_remove(reaction: Reaction, user: Union[User, Member]):
    await mainCog.handleVoteRemove(reaction, user)

@bot.check
async def globalCheck(ctx: Context):
    print(f"{ctx.message.author.name}: {ctx.message.content}")
    if ctx.channel.id in storyLinksChannelIDs:
        await ctx.message.delete()
    return True

bot.run(os.getenv("DISCORD_SECRET_PWUBOT"))
