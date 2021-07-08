
import asyncio
import datetime as dt
import discord
from discord.errors import HTTPException
from discord.ext import commands
import os
from typing import Union

from Archive import OVERARCH
from CogRetrieval import CogRetrieval
from CogMisc import CogMisc
from CogArchive import CogArchive
from CogMod import CogMod
from discordUtils import sendError, handleReaction, laprOSException
from Help import Help
from sources.general import BOT_PREFIX
import sources.text as T
import sources.ids as IDS

intents: discord.Intents = discord.Intents.default()
intents.members = True

def determinePrefix(bot: commands.Bot, message: discord.Message):
    if isinstance(message.channel, discord.DMChannel):
        if message.content.startswith(BOT_PREFIX):
            return BOT_PREFIX
        return ""
    else:
        return BOT_PREFIX

bot = commands.Bot(
    command_prefix=determinePrefix,
    case_insensitive=True,
    help_command=Help(verify_checks=False),
    intents=intents
)
archiveCog =  CogArchive(bot)
retrievalCog = CogRetrieval(bot, archiveCog)
miscCog = CogMisc(bot)
modCog = CogMod()
bot.add_cog(archiveCog)
bot.add_cog(retrievalCog)
bot.add_cog(miscCog)
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
    
    await bot.change_presence(activity=discord.Game(T.MAIN.presence))

@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    await archiveCog.handleReactionAdd(payload)

@bot.event
async def on_reaction_add(reaction: discord.Reaction, user: Union[discord.User, discord.Member]):
    if user.bot: return
    await miscCog.handleVoteAdd(reaction, user)
    await handleReaction(reaction, user)

@bot.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    await miscCog.handleVoteRemove(payload.message_id, payload.emoji, payload.user_id)

@bot.event
async def on_reaction_remove(reaction: discord.Reaction, user: Union[discord.User, discord.Member]):
    if user.bot: return
    #await handleReaction(reaction, user)

@bot.event
async def on_message_delete(message: discord.Message):
    if message.author.bot: return
    await modCog.handleMessageDelete(message)

@bot.event
async def on_message(message: discord.Message):
    if OVERARCH.isValidChannelID(message.channel.id):
        if not (message.author.id == bot.user.id and (message.content.startswith(T.ARCH.archivePostMessagePrefix) or message.content.startswith(T.ARCH.archivePostMessageWait))):
            await message.delete(delay=0.5)
    if message.author.bot: return
    
    try:
        await bot.process_commands(message)
    except laprOSException as error:
        await message.channel.send(T.UTIL.dmMessage(error.message))
        print(f"Error: {error.message}")


class MiniEntry:
    def __init__(self, userID: int, targetUserID: int, count: int):
        self.userID = userID
        self.targetUserID = targetUserID
        self.count = count

oldDeleteEntries: dict[int, MiniEntry] = {}

@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.MissingRequiredArgument):
        await sendError(ctx, T.MAIN.missingRequiredArgument(error.param.name))
    elif isinstance(error, commands.BadUnionArgument):
        await sendError(ctx, T.MAIN.badUnionArgument(error.param.name))
    elif isinstance(error, commands.TooManyArguments):
        await sendError(ctx, T.MAIN.tooManyArguments)
    elif isinstance(error, commands.CommandNotFound):
        await sendError(ctx, T.MAIN.commandNotFound)
    elif isinstance(error, commands.CommandOnCooldown):
        await sendError(ctx, T.MAIN.commandOnCooldown(int(error.retry_after)))
        return
    elif isinstance(error, commands.InvalidEndOfQuotedStringError):
        await sendError(ctx, T.MAIN.invalidEndOfQuotedStringError)
    elif isinstance(error, commands.CheckFailure):
        print(f"Error: {error}")
    elif isinstance(error, commands.CommandInvokeError):
        error: laprOSException = error.original
        if isinstance(error, laprOSException):
            await sendError(ctx, error.message)
            print(f"Error: {error.message}")
        else:
            await sendError(ctx, T.MAIN.unexpected)
            raise error
    else:
        await sendError(ctx, T.MAIN.unexpected)
        if ctx.command:
            ctx.command.reset_cooldown(ctx)
        raise error
    if ctx.command:
        ctx.command.reset_cooldown(ctx)

@bot.event
async def on_disconnect():
    OVERARCH.write()

@bot.check
async def globalCheck(ctx: commands.Context):
    channelName = ctx.channel.name if not isinstance(ctx.channel, discord.DMChannel) else "DM"
    print(f"[{str(dt.datetime.now().time())[:-7]}, #{channelName}] {ctx.message.author.name}: {ctx.message.content}")
    return True

bot.run(os.getenv("DISCORD_SECRET_PWUBOT"))
