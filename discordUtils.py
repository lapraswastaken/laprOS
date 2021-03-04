
from Archive import Archive, NotFoundException, OVERARCH
import discord
from discord.ext import commands
from discord import Embed
from sources.general import LAPROS_GRAPHIC_URL, EMPTY, stripLines
from sources.ids import BOT_USER_IDS, MOD_ROLE_IDS, MY_USER_ID
import sources.text as T
from typing import Optional, Union

class laprOSException(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

def getEmbed(title: str, description: str=None, fields: list[Union[tuple[str, str], tuple[str, str, bool]]]=None, imageURL: str=None, footer=None, url=None):
    """ Creates a custom embed. """
    
    if not description: description = ""
    if not fields: fields = []
    
    e = Embed(
        title=title,
        description=stripLines(description),
        color=0x00C0FF,
        url=url
    )
    for field in fields:
        e.add_field(
            name=field[0],
            value=EMPTY if not len(field) >= 2 else field[1],
            inline=False if not len(field) == 3 else field[2]
        )
    if imageURL:
        e.set_image(url=imageURL)
    if footer:
        e.set_footer(text=footer)
    return e

def getLaprOSEmbed(title: str, description: str=None, fields: list[Union[tuple[str, str], tuple[str, str, bool]]]=None, imageURL: str=None, footer=None, url=None):
    e = getEmbed(title, description, fields, imageURL, footer, url)
    e.set_thumbnail(url=LAPROS_GRAPHIC_URL)
    return e

async def sendError(ctx: commands.Context, errorText: str):
    """ Sends a message to the author of a command that encountered an error. """
    if canHandleArchive(ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.author.send(T.UTIL.dmMessage(errorText))
        else:
            await ctx.author.send(T.UTIL.dmMessageWithChannel(ctx.message.content[:1500], ctx.channel.id, errorText))
    else:
        await ctx.send(T.UTIL.dmMessage(errorText))
    
def fail(errorText: str):
    """ Raises a laprOSException with the given message. This gets caught in main.py and the message is sent to the user. """
    raise laprOSException(errorText)

async def fetchChannel(guild: discord.Guild, channelID: int):
    channels = await guild.fetch_channels()
    print(channels)
    print(channelID)
    return discord.utils.get(channels, id=channelID)

def canHandleArchive(ctx: commands.Context):
    """ Gets whether or not the given Context's channel can handle the CogArchive functionality. """
    
    if isinstance(ctx.channel, discord.DMChannel):
        if not OVERARCH.getGuildIDForUser(ctx.author.id):
            fail(T.UTIL.errorNoArchivePreference)
        return True
    if not OVERARCH.isValidChannelID(ctx.channel.id):
        return False
    return True

def meCheck(ctx: commands.Context):
    return ctx.author.id == MY_USER_ID
    
def isModerator(member: discord.Member):
    return any([targetID in [role.id for role in member.roles] for targetID in MOD_ROLE_IDS])

def moderatorCheck(ctx: commands.Context):
    """ Checks to see if the context's author is a moderator. """
    if isinstance(ctx.channel, discord.DMChannel):
        fail(T.UTIL.errorDMModCheck)
    return isModerator(ctx.author)

def getArchiveFromContext(ctx: commands.Context) -> Archive:
    """ Gets the Archive from the Context. If the Context's author is proxying, the proxied user's Archive is returned instead. """
    
    authorID = OVERARCH.getProxy(ctx.author.id)
    if isinstance(ctx.channel, discord.DMChannel):
        archive = OVERARCH.getArchiveForUser(authorID)
    else:
        archive = OVERARCH.getArchiveForGuild(ctx.guild.id)
        if not archive:
            fail(T.UTIL.errorNoArchiveChannel(ctx.guild.name))
    if not archive:
        fail(T.UTIL.errorNoArchivePreference)
    return archive

async def getAuthorFromContext(ctx: commands.Context) -> discord.Member:
    """ Gets the user from the Context. If the Context's author is proxying, the proxied user is returned instead. """
    
    authorID = OVERARCH.getProxy(ctx.author.id)
    guild = await getGuildFromContext(ctx)
    author = await guild.fetch_member(authorID)
    return author

async def getGuildFromContext(ctx: commands.Context) -> discord.Guild:
    
    authorID = OVERARCH.getProxy(ctx.author.id)
    if isinstance(ctx.channel, discord.DMChannel):
        guildID = OVERARCH.getGuildIDForUser(authorID)
        if not guildID:
            fail(T.UTIL.errorNoArchivePreference)
        guild = await ctx.bot.fetch_guild(guildID)
        if not guild:
            print(f"Something bad happened with {authorID}'s preferred guild ({guildID}). Has the bot been removed from that server?")
            fail(T.UTIL.errorNoGuildAccess)
    else:
        guild = ctx.guild
    return guild

async def convertMember(member: Union[discord.Member, int], ctx: Optional[commands.Context]) -> discord.Member:
    """ Returns the member argument, usually for a command. If the member argument is an int, uses the given guild to try to fetch that member. Does not take into account proxying. """
    
    if isinstance(member, int):
        guild = await getGuildFromContext(ctx) if ctx else None
        if not guild:
            fail(T.UTIL.errorNoGuild)
        member = await guild.fetch_member(member)
        if not member:
            fail(T.UTIL.errorUserIDNotFound)
    return member

def getStringArgsFromText(text: str):
    
    args: list[str] = []
    inQuote = False
    for word in text.split(" "):
        if word.startswith("\"") and not inQuote and not len(word) == 1:
            word = word[1:]
            args.append("")
            inQuote = True
        
        if inQuote:
            if word.endswith("\""):
                word = word[:-1]
                inQuote = False
            
            args[-1] = (args[-1] + f" {word}").strip()
        else:
            args.append(word)
    if inQuote:
        raise SyntaxError("Encountered end of line when parsing string")
    return args

class Page:
    def __init__(self, content: str=None, embed: Optional[discord.Embed]=None):
        self.content = content
        self.embed = embed
    
    def dump(self):
        return {
            "content": self.content,
            "embed": self.embed
        }

class Paginator:
    def __init__(self, pages: list[Page], issuerID: int, ignoreIndex: bool):
        self.pages = pages
        self.issuerID = issuerID
        self.ignoreIndex = ignoreIndex
        
        self.length = len(self.pages)
        self.focused = 0
        self.locked = False
        self.numbers = False
        
        if not self.ignoreIndex:
            for i, page in enumerate(pages):
                if not page.embed:
                    page.embed = discord.Embed(
                        title=EMPTY,
                        description=T.UTIL.paginationIndex(i + 1, self.length)
                    )
                else:
                    page.embed.set_footer(
                        text=T.UTIL.paginationIndex(i + 1, self.length)
                    )
    
    def lock(self):
        self.locked = True
    
    def unlock(self):
        self.locked = False
    
    def getReactions(self, isDM: bool):
        reactions = []
        amLarg = self.length > len(T.UTIL.indices)
        
        if self.numbers and not amLarg:
            reactions = T.UTIL.indices[:self.length]
        else:
            reactions = T.UTIL.arrows
        
        if not isDM and not amLarg:
            reactions.append(T.UTIL.switches[int(self.numbers)])
        
        return reactions
    
    def refocus(self, emoji: str):
        if emoji == T.UTIL.emojiFirst:
            self.focused = 0
        elif emoji == T.UTIL.emojiPrior and self.focused > 0:
            self.focused -= 1
        elif emoji == T.UTIL.emojiNext and self.focused < self.length - 1:
            self.focused += 1
        elif emoji == T.UTIL.emojiLast:
            self.focused = self.length - 1
            
        elif emoji in T.UTIL.indices:
            self.focused = T.UTIL.indices.index(emoji)
        elif emoji in T.UTIL.switches:
            # yes MasN this works how you think it does
            self.numbers = not self.numbers
        
        return self.getFocused()
    
    def getFocused(self):
        return self.pages[self.focused]

toListen: dict[int, Paginator] = {}
        
async def updatePaginatedMessage(message: discord.Message, user: discord.User, paginator: Paginator, emoji: Optional[str]=None):
    if not user.id == paginator.issuerID: return
    oldFocused = paginator.getFocused()
    focused = paginator.refocus(emoji)
    if not oldFocused is focused:
        await message.edit(content=focused.content, embed=focused.embed)
    isDM = isinstance(message.channel, discord.DMChannel)
    if emoji in T.UTIL.switches and not isDM:
        newReactions = paginator.getReactions(isDM)
        await message.clear_reactions()
        for reaction in newReactions:
            await message.add_reaction(reaction)
    elif emoji == None:
        newReactions = paginator.getReactions(isDM)
        for reaction in newReactions:
            await message.add_reaction(reaction)
        

async def paginate(ctx: commands.Context, contents: list[dict[str, Union[str, discord.Embed]]], ignoreIndex: bool=False):
    pages = []
    for page in contents:
        pages.append(Page(**page))
    if not pages:
        raise IndexError("No messages were given to the pagination function")
    
    paginator = Paginator(pages, ctx.author.id, ignoreIndex)
    focused = paginator.getFocused()
    message: discord.Message = await ctx.send(content=focused.content, embed=focused.embed)
    toListen[message.id] = paginator
    await updatePaginatedMessage(message, ctx.author, paginator)

async def handleReaction(reaction: discord.Reaction, user: Union[discord.Member, discord.User]):
    if not reaction.message.id in toListen:
        return
    paginator = toListen[reaction.message.id]
    
    emoji = str(reaction.emoji)
    await updatePaginatedMessage(reaction.message, user, paginator, emoji)
    if not isinstance(reaction.message.channel, discord.DMChannel):
        await reaction.remove(user)
