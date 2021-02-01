
import datetime
import discord
from discord.ext import commands
from discordUtils import dmError
import os
from typing import Union

from Archive import OVERARCH
from CogRetrieval import CogRetrieval
from CogMain import CogMain
from CogArchive import CogArchive
from CogMod import CogMod
import sources.general as T_GEN
import sources.textArchive as T_ARCH
import sources.textErrors as T_ERR

bot = commands.Bot(
    command_prefix=T_GEN.prefix,
    case_insensitive=True,
    help_command=commands.DefaultHelpCommand(verify_checks=False)
)
mainCog = CogMain(bot)
storyCog =  CogArchive()
archiveCog = CogRetrieval()
modCog = CogMod()
bot.add_cog(mainCog)
bot.add_cog(storyCog)
bot.add_cog(archiveCog)
bot.add_cog(modCog)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}.")
    guild: discord.Guild
    for guild in bot.guilds:
        try:
            await modCog.handleOnReady(guild)
        except discord.Forbidden:
            print(f"Missing permission to view audit logs in {guild.name}")

@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    await CogArchive.handleReactionAdd(payload)

@bot.event
async def on_reaction_add(reaction: discord.Reaction, user: Union[discord.User, discord.Member]):
    if user.bot: return
    await mainCog.handleVoteAdd(reaction, user)

@bot.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    await mainCog.handleVoteRemove(payload.message_id, payload.emoji, payload.user_id)

@bot.event
async def on_message_delete(message: discord.Message):
    if message.author.bot: return
    await mainCog.handleMessageDelete(message)
    await modCog.handleMessageDelete(message)

@bot.event
async def on_message(message: discord.Message):
    if OVERARCH.isValidChannelID(message.channel.id):
        if not (message.author.id == bot.user.id and (message.content.startswith(T_ARCH.messagePrefix) or message.content.startswith(T_ARCH.messageWait))):
            await message.delete(delay=0.5)
    if message.author.bot: return
    await bot.process_commands(message)
    
@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.MissingRequiredArgument):
        await dmError(ctx, T_ERR.missingRequiredArgument(error.param.name))
    elif isinstance(error, commands.TooManyArguments):
        await dmError(ctx, T_ERR.tooManyArguments)
    elif isinstance(error, commands.CommandNotFound):
        await dmError(ctx, T_ERR.commandNotFound)
    elif isinstance(error, commands.CommandOnCooldown):
        await dmError(ctx, T_ERR.commandOnCooldown(int(error.retry_after)))
        return
    elif isinstance(error, commands.InvalidEndOfQuotedStringError):
        await dmError(ctx, T_ERR.invalidEndOfQuotedStringError)
        return
    elif isinstance(error, commands.CheckFailure):
        return
    else:
        await dmError(ctx, T_ERR.unexpected)
        raise error
    if ctx.command:
        ctx.command.reset_cooldown(ctx)

@bot.event
async def on_disconnect():
    OVERARCH.write()

@bot.check
async def globalCheck(ctx: commands.Context):
    print(f"[{str(datetime.datetime.now().time())[:-7]}] {ctx.message.author.name}: {ctx.message.content}")
    return True

bot.run(os.getenv("DISCORD_SECRET_PWUBOT"))
