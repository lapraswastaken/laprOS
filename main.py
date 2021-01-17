
from ArchiveCog import ArchiveCog
import discord
from discord.ext import commands
from discordUtils import dmError
from MainCog import MainCog
import os
from StoryCog import StoryCog
from typing import Union

storyLinksChannelIDs = [794355705368018954, 792629600860897330, 798023111453966347]

bot = commands.Bot(command_prefix="lap.", case_insensitive=True, help_command=commands.DefaultHelpCommand(verify_checks=False))
mainCog = MainCog(bot)
bot.add_cog(mainCog)
bot.add_cog(StoryCog(bot, storyLinksChannelIDs))
bot.add_cog(ArchiveCog(bot))

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}.")

@bot.event
async def on_reaction_add(reaction: discord.Reaction, user: Union[discord.User, discord.Member]):
    await mainCog.handleVoteAdd(reaction, user)

@bot.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    await mainCog.handleVoteRemove(payload.message_id, payload.emoji, payload.user_id)

@bot.event
async def on_message(message: discord.Message):
    if message.channel.id in storyLinksChannelIDs:
        if not (message.author.id == bot.user.id and message.content.startswith("**Writer**:")):
            await message.delete()
    await bot.process_commands(message)
    
@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.MissingRequiredArgument):
        await dmError(ctx, f"You missed an argument that is required to use this command: {error.param.name}")
    elif isinstance(error, commands.TooManyArguments):
        await dmError(ctx, "You gave this command too many arguments. Make sure you're surrounding arguments that have spaces in them with quotes (space is the delimiter for arguments).")
    elif isinstance(error, commands.CommandNotFound):
        await dmError(ctx, "This command doesn't exist!")
    elif isinstance(error, commands.CommandOnCooldown):
        await dmError(ctx, f"This command is on cooldown right now. Please wait {int(error.retry_after)} seconds and try again.")
        return
    else:
        await dmError(ctx, "An unexpected error occurred. Please let @lapras know.")
        raise error
    ctx.command.reset_cooldown(ctx)

@bot.check
async def globalCheck(ctx: commands.Context):
    print(f"{ctx.message.author.name}: {ctx.message.content}")
    return True

bot.run(os.getenv("DISCORD_SECRET_PWUBOT"))
