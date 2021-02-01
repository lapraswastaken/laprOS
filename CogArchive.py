
from Story import getStoriesFromMessage
from typing import Callable, Optional, Union
import discord
from discord.ext import commands
from discordUtils import dmError, dmErrorAndRaise, getEmbed, getStringArgsFromText, moderatorCheck
import re
from Archive import Story, DuplicateException, InvalidNameException, MaxLenException, MaxNameLenException, MaxSpeciesLenException, NotFoundException, OVERARCH, Post
import sources.textArchive as T_ARCH
import sources.general as T_GEN

digitsPat = re.compile(r"(\d+)")

reactionLockedMessageIDs: list[int] = []

class CogArchive(commands.Cog, name=T_ARCH.cogName, description=T_ARCH.cogDescription):
    
    def __init__(self):
        self.proxies: dict[int, discord.Member] = {}
    
    async def cog_check(self, ctx: commands.Context):
        if not OVERARCH.isValidChannelID(ctx.channel.id):
            await ctx.send(content=T_ARCH.errorNotInArchiveChannel)
            return False
        return True
    
    async def checkIsMemberProxied(self, author: discord.Member) -> discord.Member:
        if not author.id in self.proxies:
            return author
        return await author.guild.fetch_member(self.proxies[author.id].id)
    
    @staticmethod
    async def handleReactionAdd(payload: discord.RawReactionActionEvent):
        if payload.message_id in reactionLockedMessageIDs: return
        
        archive = OVERARCH.getArchive(payload.guild_id)
        if (not archive) or (not payload.member) or (payload.member.bot): return
        
        archiveChannel: discord.TextChannel = payload.member.guild.get_channel(payload.channel_id)
        message: discord.Message = await archiveChannel.fetch_message(payload.message_id)
        
        try:
            post = archive.getPostByMessageID(payload.message_id)
        except NotFoundException:
            return
        
        emoji = str(payload.emoji)
        
        if emoji == T_ARCH.firstEmoji:
            post.focused = 0
        elif emoji == T_ARCH.priorEmoji and post.focused > 0:
            post.focused -= 1
        elif emoji == T_ARCH.nextEmoji and post.focused < len(post.stories) - 1:
            post.focused += 1
        elif emoji == T_ARCH.lastEmoji:
            post.focused = len(post.stories) - 1
        
        await CogArchive.updateFocusedStory(message, post)
        
    @staticmethod
    async def updateFocusedStory(message: discord.Message, post: Post):
        reactionLockedMessageIDs.append(message.id)
        
        story = post.getFocusedStory()
        if len(post.stories) > 1:
            await message.edit(
                content=T_ARCH.messageBody(post.authorID, story.format()[:1800]),
                embed=getEmbed(T_ARCH.embedTitle, T_ARCH.embedDescription(post.format()))
            )
        else:
            await message.edit(
                content=T_ARCH.messageBody(post.authorID, story.format()[:1800]),
                embed=None
            )
        
        await message.clear_reactions()
        if post.focused > 0:
            if len(post.stories) > 2:
                await message.add_reaction(T_ARCH.firstEmoji)
            await message.add_reaction(T_ARCH.priorEmoji)
        if post.focused < len(post.stories) - 1:
            await message.add_reaction(T_ARCH.nextEmoji)
            if len(post.stories) > 2:
                await message.add_reaction(T_ARCH.lastEmoji)
        
        reactionLockedMessageIDs.remove(message.id)
    
    @staticmethod
    async def getArchive(ctx: commands.Context):
        archive = OVERARCH.getArchive(ctx.guild.id)
        if not archive:
            await dmError(ctx, T_ARCH.errorNoArchiveChannel)
            raise commands.CheckFailure()
        return archive
        
    @staticmethod
    async def updateArchivePost(archiveChannel: discord.TextChannel, post: Post, story: Optional[Story]):
        """ Updates the messages in a give archive text channel that make up a given post. """
        if not story: # this happens when deleting a story
            # focus the first story for the author if it exists
            print("Updating post for deleted story")
            if post.stories:
                print("Focusing first story and updating")
                story = post.stories[0]
            # if the deleted story was the only one that the author had, delete the message and reset the ID on the post
            elif post.messageID:
                print("Deleted story was the last in the post, deleting message")
                message = await archiveChannel.fetch_message(post.messageID)
                await message.delete()
                post.messageID = None
                return
            # this shouldn't happen
            else:
                print("Deleted a story for a post with a nonexistent message ID. How does that work...?")
                return
        
        try:
            message = await archiveChannel.fetch_message(post.messageID)
        except (discord.NotFound, discord.HTTPException):
            message: discord.Message = await archiveChannel.send(T_ARCH.messageWait)
            await message.add_reaction(T_ARCH.firstEmoji)
            await message.add_reaction(T_ARCH.priorEmoji)
            await message.add_reaction(T_ARCH.nextEmoji)
            await message.add_reaction(T_ARCH.lastEmoji)
            post.messageID = message.id
        
        post.focusStory(story)
        await CogArchive.updateFocusedStory(message, post)
    
    async def getPostAuthorArchive(self, ctx: commands.Context, error: bool=True):
        author = await self.checkIsMemberProxied(ctx.author)
        archive = await CogArchive.getArchive(ctx)
        post = archive.getPost(author.id)
        if error and not post:
            await dmErrorAndRaise(ctx, T_ARCH.errorNoPost)
            return
        return post, author, archive
    
    async def setStoryAttr(self, ctx: commands.Context, targetTitle: str, changer: Callable[[Story], None]):
        post, *_ = await self.getPostAuthorArchive(ctx)
        
        try:
            story = post.getStory(targetTitle)
        except NotFoundException:
            await dmErrorAndRaise(ctx, T_ARCH.errorNoStory(targetTitle))
            return
        
        await changer(story)
        
        await CogArchive.updateArchivePost(ctx.channel, post, story)
        OVERARCH.write()
    
    @commands.command(ignore_extra=False, hidden=True)
    @commands.check(moderatorCheck)
    async def proxyuser(self, ctx: commands.Context, member: Union[discord.Member, int]):
        if isinstance(member, discord.Member):
            self.proxies[ctx.author.id] = member
        else:
            self.proxies[ctx.author.id] = await ctx.guild.get_member(member)
    
    @commands.command(ignore_extra=False, hidden=True)
    @commands.check(moderatorCheck)
    async def clearproxy(self, ctx: commands.Context):
        if ctx.author.id in self.proxies:
            self.proxies.pop(ctx.author.id)
        
    @commands.command()
    async def multi(self, ctx: commands.Context, *, allTextCommands: str):
        """ Performs multiple commands (split apart by newlines) at once. Thanks to love for laying the groundwork for this command. """
        
        allTextCommands = [command if not command.startswith(T_GEN.prefix) else command[len(T_GEN.prefix):] for command in allTextCommands.split("\n")]
        
        for textCommand in allTextCommands:
            targetCmdName: str = None
            args: list[str] = None
            try:
                targetCmdName, *args = getStringArgsFromText(textCommand)
            except SyntaxError:
                await dmErrorAndRaise(ctx, f"There was an issue with the quotes in your command: `{textCommand}`")
            
            commandFn: commands.Command
            found = False
            for commandFn in self.get_commands():
                if targetCmdName == commandFn.name:
                    try:
                        print(f"running command {targetCmdName}")
                        await commandFn(ctx, *args)
                        found = True
                    except TypeError:
                        await dmErrorAndRaise(ctx, T_ARCH.errorNumberArgs(targetCmdName))
                        raise
                    break
            
            if not found:
                await dmErrorAndRaise(ctx, T_ARCH.errorInvalidCommand(targetCmdName))
            
    @commands.command(ignore_extra=False)
    #@commands.cooldown(1, 8 * 60, commands.BucketType.guild)
    async def addstory(self, ctx: commands.Context, storyTitle: str):
        """ Adds a new story with the given title to the story links post for the command issuer.
            If no such post exists, creates one. 
            All other values except for title are left blank and must be altered with their respective .set commands. """
        post, author, archive = await self.getPostAuthorArchive(ctx, False)
        if not post:
            post = archive.createPost(author.id)
        
        try:
            newStory = Story(storyTitle)
            post.addStory(newStory)
        except MaxLenException:
            await dmErrorAndRaise(ctx, T_ARCH.errorLenTitle); return
        except DuplicateException:
            await dmErrorAndRaise(ctx, T_ARCH.errorDupStory(storyTitle)); return
        await CogArchive.updateArchivePost(ctx.channel, post, newStory)
        OVERARCH.write()
    
    @commands.command(ignore_extra=False)
    async def removestory(self, ctx: commands.Context, targetTitle: str):
        """ Removes the story with the given title. """
        post, *_ = await self.getPostAuthorArchive(ctx)
        
        try:
            post.removeStory(targetTitle)
        except NotFoundException:
            await dmErrorAndRaise(ctx, T_ARCH.errorNoStory(targetTitle))
            
        await CogArchive.updateArchivePost(ctx.channel, post, None)
        OVERARCH.write()
    
    @commands.command(ignore_extra=False)
    async def settitle(self, ctx: commands.Context, newTitle: str, targetTitle: str=None):
        """ Sets the title of the latest-added story of the issuer.
            if targetTitle is specified, sets the title of that story instead (this is somewhat unintuitive - the first parameter is still the new name of the story). """
            
        async def changeTitle(story: Story):
            try:
                story.setTitle(newTitle)
            except MaxLenException:
                await dmErrorAndRaise(ctx, T_ARCH.errorLenTitle)
        await self.setStoryAttr(ctx, targetTitle, changeTitle)

    @commands.command(ignore_extra=False)
    async def addgenre(self, ctx: commands.Context, newGenre: str, targetTitle: str=None):
        """ Adds a genre to the latest-added story of the issuer.
            If targetTitle is specified, adds the genre to that story instead. """
        
        async def changeGenre(story: Story):
            try:
                story.addGenre(newGenre.capitalize())
                print(f"Added {newGenre} genre to {story.cite()}.")
            except InvalidNameException:
                await dmErrorAndRaise(ctx, T_ARCH.errorInvalidGenre(newGenre))
            except DuplicateException:
                await dmErrorAndRaise(ctx, T_ARCH.errorDupGenre(story.cite(), newGenre))
        await self.setStoryAttr(ctx, targetTitle, changeGenre)
    
    @commands.command(ignore_extra=False)
    async def removegenre(self, ctx: commands.Context, targetGenre: str, targetTitle: str=None):
        """ Removes the specified genre from the latest-added story of the issuer.
            If targetTitle is specified, removes the genre from that story instead. """
        
        async def changeGenre(story: Story):
            try:
                story.removeGenre(targetGenre)
                print(f"Removed {targetGenre} genre from {story.cite()}.")
            except NotFoundException:
                await dmErrorAndRaise(ctx, T_ARCH.errorNoGenre(story.cite(), targetGenre))
        await self.setStoryAttr(ctx, targetTitle, changeGenre)
    
    @commands.command(ignore_extra=False)
    async def setrating(self, ctx: commands.Context, newRating: str, targetTitle: str=None):
        """ Sets the rating for the latest-added story of the issuer.
            If targetTitle is specified, sets the rating for that story instead. """
        
        async def changeRating(story: Story):
            try:
                story.setRating(newRating)
                print(f"Set rating of {story.cite()} to {newRating}.")
            except InvalidNameException:
                await dmErrorAndRaise(ctx, T_ARCH.errorInvalidRating(story.cite(), newRating))
        await self.setStoryAttr(ctx, targetTitle, changeRating)
    
    @commands.command(ignore_extra=False)
    async def setratingreason(self, ctx: commands.Context, newReason: str, targetTitle: str=None):
        """ Sets the rating reason for the latest-added story of the issuer.
            If targetTitle is specified, sets the rating reason for that story instead. """
        
        async def changeReason(story: Story):
            try:
                story.setRatingReason(newReason)
                print(f"Set rating reason of {story.cite()} to {newReason}.")
            except MaxLenException:
                await dmErrorAndRaise(ctx, T_ARCH.errorLenReason)
        await self.setStoryAttr(ctx, targetTitle, changeReason)

    @commands.command(ignore_extra=False)
    async def addcharacter(self, ctx: commands.Context, newCharSpecies: str, newCharName: str="", targetTitle: str=None):
        """ Adds a character with the given species and optional nickname to the latest-added story of the issuer.
            A species can be given to the character with the charSpecies parameter. If this needs to be omitted so that a speciesless character can be added to a specific story, an empty string ("") can be passed.
            If targetTitle is specified, adds a character to that story instead. """
        
        async def changeCharacter(story: Story):
            try:
                story.addCharacter(newCharSpecies, newCharName)
                print(f"Added character with species {newCharSpecies} and name {newCharName} to {story.cite()}.")
            except DuplicateException:
                andName = "" if not newCharName else f" and the name {newCharName}."
                await dmErrorAndRaise(ctx, T_ARCH.errorDupChar(story.cite(), newCharSpecies, newCharName))
            except MaxSpeciesLenException:
                await dmErrorAndRaise(ctx, T_ARCH.errorLenCharSpecies)
            except MaxNameLenException:
                await dmErrorAndRaise(ctx, T_ARCH.errorLenCharName)
        await self.setStoryAttr(ctx, targetTitle, changeCharacter)
    
    @commands.command(ignore_extra=False)
    async def removecharacter(self, ctx: commands.Context, targetCharSpecies: str, targetCharName: str="", targetTitle: str=None):
        """ Removes a character with the given species from the latest-added story of the issuer.
            If targetTitle is specified, removes a character from that story instead. """
        
        async def changeCharacter(story: Story):
            try:
                story.removeCharacter(targetCharSpecies, targetCharName)
                print(f"Removed character with species {targetCharSpecies} and name {targetCharName} from {story.cite()}.")
            except NotFoundException:
                await dmErrorAndRaise(ctx, T_ARCH.errorNoChar(story.cite(), targetCharSpecies, targetCharName))
        await self.setStoryAttr(ctx, targetTitle, changeCharacter)
    
    @commands.command(ignore_extra=False)
    async def setsummary(self, ctx: commands.Context, newSummary: str, targetTitle: str=None):
        """ Sets the summary of the latest-added story of the issuer.
            If targetTitle is specified, sets the summary of that story instead. """
        
        async def changeSummary(story: Story):
            try:
                story.setSummary(newSummary)
                print(f"Set summary of {story.cite()} to:\n{newSummary}")
            except MaxLenException:
                await dmErrorAndRaise(ctx, T_ARCH.errorLenSummary)
        await self.setStoryAttr(ctx, targetTitle, changeSummary)
    
    @commands.command(ignore_extra=False)
    async def addlink(self, ctx: commands.Context, linkSiteAbbr: str, linkURL: str, targetTitle: str=None):
        """ Adds a link with the given site abbreviation and URL to the latest-added story of the issuer.
            If targetTitle is specified, adds the link to that story instead. """
        
        async def changeLink(story: Story):
            try:
                story.addLink(linkSiteAbbr, linkURL)
            except InvalidNameException:
                await dmErrorAndRaise(ctx, T_ARCH.errorInvalidLinkAbbr(story.cite(), linkSiteAbbr))
            except DuplicateException:
                await dmErrorAndRaise(ctx, T_ARCH.errorDupLink(story.cite(), linkSiteAbbr))
            except MaxLenException:
                await dmErrorAndRaise(ctx, T_ARCH.errorLenLinkURL)
        await self.setStoryAttr(ctx, targetTitle, changeLink)
    
    @commands.command(ignore_extra=False)
    async def removelink(self, ctx: commands.Context, targetSiteAbbr: str, targetTitle: str=None):
        """ Removes the link with the given name from the latest-added story of the issuer.
            If targetTitle is specified, removes the link from that story instead. """
        
        async def changeLink(story: Story):
            try:
                story.removeLink(targetSiteAbbr)
            except NotFoundException:
                await dmErrorAndRaise(ctx, T_ARCH.errorNoLink(story.cite(), targetSiteAbbr))
        await self.setStoryAttr(ctx, targetTitle, changeLink)
    
    @commands.command(hidden=True)
    @commands.check(moderatorCheck)
    async def convert(self, ctx: commands.Context, limit: int=None):
        """ Adds each story in the archive channel this command is used in to the JSON database. """
        
        message: discord.Message
        async for message in ctx.channel.history(limit=limit):
            try:
                author, oldStories = await getStoriesFromMessage(message)
            except discord.NotFound:
                print("Couldn't find member for this message")
                continue
            if not oldStories: continue
            archive = await CogArchive.getArchive(ctx)
            post = archive.getPost(author.id)
            if not post:
                post = archive.createPost(author.id)
                post.messageID = message.id
            else:
                await message.delete()
            for story in oldStories:
                try:
                    post.addStory(story)
                except DuplicateException:
                    continue
            await self.updateArchivePost(ctx.channel, post, None)

    @commands.command(hidden=True)
    @commands.check(moderatorCheck)
    async def updatepost(self, ctx: commands.Context):
        async def dummy(_): pass
        await self.setStoryAttr(ctx, None, dummy)
