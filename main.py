
from ArchiveCog import ArchiveCog
from discord.ext.commands.help import DefaultHelpCommand, HelpCommand
from discord.raw_models import RawReactionActionEvent
from StoryCog import StoryCog
from typing import Union
from discord.ext.commands import Bot
from discord.ext.commands.context import Context
from discord.member import Member
from discord.message import Message
from discord.reaction import Reaction
from discord.user import User
import os
from MainCog import MainCog

storyLinksChannelIDs = [794355705368018954, 792629600860897330, 798023111453966347]

bot = Bot(command_prefix="lap.", case_insensitive=True, help_command=DefaultHelpCommand(verify_checks=False))
mainCog = MainCog(bot)
bot.add_cog(mainCog)
bot.add_cog(StoryCog(bot, storyLinksChannelIDs))
bot.add_cog(ArchiveCog(bot))

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}.")

@bot.event
async def on_reaction_add(reaction: Reaction, user: Union[User, Member]):
    await mainCog.handleVoteAdd(reaction, user)

@bot.event
async def on_raw_reaction_remove(payload: RawReactionActionEvent):
    await mainCog.handleVoteRemove(payload.message_id, payload.emoji, payload.user_id)

@bot.event
async def on_message(message: Message):
    await bot.process_commands(message)
    if message.channel.id in storyLinksChannelIDs:
        if not (message.author.id == bot.user.id and message.content.startswith("**Writer**:")):
            await message.delete()

@bot.check
async def globalCheck(ctx: Context):
    print(f"{ctx.message.author.name}: {ctx.message.content}")
    return True

bot.run(os.getenv("DISCORD_SECRET_THE_ANNOUNCER"))
