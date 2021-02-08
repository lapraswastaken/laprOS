
from Archive import OVERARCH
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

async def dm(ctx: commands.Context, errorText: str):
    """ Sends a message to the author of a command that encountered an error. """
    if isinstance(ctx.channel, discord.DMChannel):
        await ctx.author.send(T.UTIL.dmMessage(errorText))
    else:
        await ctx.author.send(T.UTIL.dmMessageWithChannel(ctx.message.content[:1500], ctx.channel.id, errorText))
    
def fail(errorText: str):
    """ Sends a message to the author of a command that encountered an error, then raises a commands.CheckFailure. """
    raise laprOSException(errorText)

async def getGuildFromCtx(ctx: commands.Context) -> Optional[discord.Guild]:
    if isinstance(ctx.channel, discord.DMChannel):
        matched: list[int] = []
        for guildID, archive in OVERARCH.archives.items():
            for authorID in archive.posts:
                if authorID == ctx.author.id:
                    matched.append(guildID)
        
        if len(matched) == 1:
            return await ctx.bot.fetch_guild(*matched)
        else:
            archivePref = OVERARCH.userArchivePrefs.get(ctx.author.id)
            if not archivePref:
                fail()

def checkIsBotID(id: int):
    return id in BOT_USER_IDS
    
def meCheck(ctx: commands.Context):
    return ctx.author.id == MY_USER_ID

def moderatorCheck(ctx: commands.Context):
    """ Checks to see if the context's author is a moderator. """
    
    return [targetID in [role.id for role in ctx.author.roles] for targetID in MOD_ROLE_IDS]

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
    
    def amLarg(self):
        return self.length > len(T.UTIL.indices)
    
    def canUseNumbers(self):
        return self.numbers and not self.amLarg()
    
    def getReactions(self):
        reactions: list[str] = []
        amBig = self.length > 3
        
        if self.canUseNumbers():
            reactions = T.UTIL.indices[:self.length]
        else:
            if self.focused > 0:
                if amBig:
                    reactions.append(T.UTIL.emojiFirst)
                reactions.append(T.UTIL.emojiPrior)
            if self.focused < self.length - 1:
                reactions.append(T.UTIL.emojiNext)
                if amBig:
                    reactions.append(T.UTIL.emojiLast)
        if self.amLarg():
            return reactions
        return reactions + ([T.UTIL.emojiNumbers] if not self.numbers else [T.UTIL.emojiArrows])
    
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
        elif emoji in [T.UTIL.emojiNumbers, T.UTIL.emojiArrows]:
            self.numbers = not self.numbers
    
    def getFocused(self):
        return self.pages[self.focused]

toListen: dict[int, Paginator] = {}
        
async def updatePaginatedMessage(message: discord.Message, user: discord.User, paginator: Paginator, emoji: Optional[str]=None):
    paginator.refocus(emoji)
    focused = paginator.getFocused()
    await message.edit(content=focused.content, embed=focused.embed)
    if not paginator.canUseNumbers() or (not emoji) or emoji == T.UTIL.emojiNumbers:
        paginator.lock()
        await message.clear_reactions()
        reactions = paginator.getReactions()
        for reaction in reactions:
            await message.add_reaction(reaction)
        paginator.unlock()
    else:
        await message.remove_reaction(emoji, user)

async def paginate(ctx: commands.Context, contents: list[dict[str, Union[str, discord.Embed]]], dm: bool=False, ignoreIndex: bool=False):
    pages = []
    for page in contents:
        pages.append(Page(**page))
    if not pages:
        raise IndexError("No messages were given to the pagination function")
    if not dm:
        paginator = Paginator(pages, ctx.author.id, ignoreIndex)
        focused = paginator.getFocused()
        message: discord.Message = await ctx.send(content=focused.content, embed=focused.embed)
        toListen[message.id] = paginator
        await updatePaginatedMessage(message, ctx.author, paginator)

async def handleReactionAdd(reaction: discord.Reaction, user: Union[discord.Member, discord.User]):
    if not reaction.message.id in toListen:
        return
    paginator = toListen[reaction.message.id]
    if paginator.locked or user.id != paginator.issuerID:
        return
    
    emoji = str(reaction.emoji)
    await updatePaginatedMessage(reaction.message, user, paginator, emoji)
