
from Story import getStoriesFromMessage
from typing import Callable, Optional, Union
import discord
from discord.ext import commands
from discordUtils import dmError, dmErrorAndRaise, getEmbed, getStringArgsFromText, moderatorCheck
import re
from Archive import Story, DuplicateException, InvalidNameException, MaxLenException, MaxNameLenException, MaxSpeciesLenException, NotFoundException, OVERARCH, Post
import sources.text as T
from sources.general import BOT_PREFIX

reactionLockedMessageIDs: list[int] = []

class CogArchive(commands.Cog, name=T.ARCH.cogName, description=T.ARCH.cogDescription):
    
    def __init__(self):
        self.proxies: dict[int, discord.Member] = {}
    
    async def cog_check(self, ctx: commands.Context):
        if not OVERARCH.isValidChannelID(ctx.channel.id):
            await ctx.send(content=T.ARCH.errorNotInArchiveChannel)
            return False
        return True
    
    async def checkIsMemberProxied(self, author: discord.Member) -> discord.Member:
        if not author.id in self.proxies:
            return author
        return await author.guild.fetch_member(self.proxies[author.id].id)
    
    @staticmethod
    async def parseCharacter(ctx: commands.Context, text: str) -> tuple[str, str]:
        """ Gets the character name (optional, may be empty string) and the character species from a string. """
        parts = [part.strip() for part in text.split("|", 1)]
        print(parts)
        if not parts[0]:
            await dmErrorAndRaise(ctx, T.ARCH.errorCharacterNoSpecies)
        if len(parts) == 2:
            return parts[0], " ".join([word.capitalize() for word in parts[1].split(" ")])
        else:
            return "", " ".join([word.capitalize() for word in parts[0].split(" ")])
    
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
        
        if emoji == T.ARCH.firstEmoji:
            post.focused = 0
        elif emoji == T.ARCH.priorEmoji and post.focused > 0:
            post.focused -= 1
        elif emoji == T.ARCH.nextEmoji and post.focused < len(post.stories) - 1:
            post.focused += 1
        elif emoji == T.ARCH.lastEmoji:
            post.focused = len(post.stories) - 1
        
        await CogArchive.updateFocusedStory(message, post)
        
    @staticmethod
    async def updateFocusedStory(message: discord.Message, post: Post):
        """ Edits the message with the formatted contents of the post and refreshes its pagination reactions. """
        
        reactionLockedMessageIDs.append(message.id)
        
        story = post.getFocusedStory()
        if len(post.stories) > 1:
            await message.edit(
                content=T.ARCH.archivePostMessageBody(post.authorID, story.format()[:1800]),
                embed=getEmbed(T.ARCH.archivePostEmbedTitle, T.ARCH.archivePostEmbedDescription(post.format()))
            )
        else:
            await message.edit(
                content=T.ARCH.archivePostMessageBody(post.authorID, story.format()[:1800]),
                embed=None
            )
        
        await message.clear_reactions()
        if post.focused > 0:
            if len(post.stories) > 2:
                await message.add_reaction(T.ARCH.firstEmoji)
            await message.add_reaction(T.ARCH.priorEmoji)
        if post.focused < len(post.stories) - 1:
            await message.add_reaction(T.ARCH.nextEmoji)
            if len(post.stories) > 2:
                await message.add_reaction(T.ARCH.lastEmoji)
        
        reactionLockedMessageIDs.remove(message.id)
    
    @staticmethod
    async def getArchive(ctx: commands.Context):
        """ Gets the Archive object associated with a context's guild. """
        
        archive = OVERARCH.getArchive(ctx.guild.id)
        if not archive:
            await dmError(ctx, T.ARCH.errorNoArchiveChannel)
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
            message: discord.Message = await archiveChannel.send(T.ARCH.archivePostMessageWait)
            await message.add_reaction(T.ARCH.firstEmoji)
            await message.add_reaction(T.ARCH.priorEmoji)
            await message.add_reaction(T.ARCH.nextEmoji)
            await message.add_reaction(T.ARCH.lastEmoji)
            post.messageID = message.id
        
        post.focusStory(story)
        await CogArchive.updateFocusedStory(message, post)
    
    async def getPostAuthorArchive(self, ctx: commands.Context, error: bool=True):
        """ Gets the post, the author, and the archive from the context. If `error`, if a post isn't found, the context is notified and an error is thrown. """
        
        author = await self.checkIsMemberProxied(ctx.author)
        archive = await CogArchive.getArchive(ctx)
        post = archive.getPost(author.id)
        if error and not post:
            await dmErrorAndRaise(ctx, T.ARCH.errorNoPost)
            return
        return post, author, archive
    
    async def setStoryAttr(self, ctx: commands.Context, changer: Callable[[Story], None]):
        """ Calls the `changer` function on the currently focused story in the post linked to the context. """
        
        post, *_ = await self.getPostAuthorArchive(ctx)

        story = post.getFocusedStory()
        
        await changer(story)
        
        await CogArchive.updateArchivePost(ctx.channel, post, story)
        OVERARCH.write()
    
    @commands.command(**T.ARCH.cmd.proxyUser, ignore_extra=False, hidden=True)
    @commands.check(moderatorCheck)
    async def proxyUser(self, ctx: commands.Context, member: Union[discord.Member, int]):
        if isinstance(member, discord.Member):
            self.proxies[ctx.author.id] = member
        else:
            self.proxies[ctx.author.id] = await ctx.guild.get_member(member)
    
    @commands.command(**T.ARCH.cmd.clearProxy, ignore_extra=False, hidden=True)
    @commands.check(moderatorCheck)
    async def clearProxy(self, ctx: commands.Context):
        if ctx.author.id in self.proxies:
            self.proxies.pop(ctx.author.id)
        
    @commands.command(**T.ARCH.cmd.multi)
    async def multi(self, ctx: commands.Context, *, allTextCommands: str):
        # thank you, love
        
        allTextCommands = [command if not command.startswith(BOT_PREFIX) else command[len(BOT_PREFIX):] for command in allTextCommands.split("\n")]
        
        for textCommand in allTextCommands:
            targetCmdName: str = None
            args: list[str] = None
            try:
                targetCmdName, *args = getStringArgsFromText(textCommand)
            except SyntaxError:
                await dmErrorAndRaise(ctx, T.ARCH.errorMultiQuotes(textCommand))
            
            commandFn: commands.Command
            found = False
            for commandFn in self.get_commands():
                if targetCmdName.lower() == commandFn.name or targetCmdName.lower() in commandFn.aliases:
                    try:
                        print(f"running command {targetCmdName}")
                        await commandFn(ctx, *args)
                        found = True
                    except TypeError as e:
                        await dmError(ctx, T.ARCH.errorNumberArgs(targetCmdName))
                        raise e
                    break
            
            if not found:
                await dmErrorAndRaise(ctx, T.ARCH.errorInvalidCommand(targetCmdName))
            
    @commands.command(**T.ARCH.cmd.addStory, ignore_extra=False)
    @commands.cooldown(1, 8 * 60, commands.BucketType.guild)
    async def addStory(self, ctx: commands.Context, *storyTitle: str):
        storyTitle = " ".join(storyTitle)
        
        post, author, archive = await self.getPostAuthorArchive(ctx, False)
        if not post:
            post = archive.createPost(author.id)
        
        try:
            newStory = Story(storyTitle)
            post.addStory(newStory)
        except MaxLenException:
            await dmErrorAndRaise(ctx, T.ARCH.errorLenTitle); return
        except DuplicateException:
            await dmErrorAndRaise(ctx, T.ARCH.errorDupStory(storyTitle)); return
        await CogArchive.updateArchivePost(ctx.channel, post, newStory)
        OVERARCH.write()
    
    @commands.command(**T.ARCH.cmd.removeStory, ignore_extra=False)
    async def removeStory(self, ctx: commands.Context, targetTitle: str):
        post, *_ = await self.getPostAuthorArchive(ctx)
        
        try:
            post.removeStory(targetTitle)
        except NotFoundException:
            await dmErrorAndRaise(ctx, T.ARCH.errorNoStory(targetTitle))
            
        await CogArchive.updateArchivePost(ctx.channel, post, None)
        OVERARCH.write()
    
    @commands.command(**T.ARCH.cmd.setTitle)
    async def setTitle(self, ctx: commands.Context, *newTitle: str):
        newTitle = " ".join(newTitle)
            
        async def changeTitle(story: Story):
            try:
                story.setTitle(newTitle)
            except MaxLenException:
                await dmErrorAndRaise(ctx, T.ARCH.errorLenTitle)
        await self.setStoryAttr(ctx, changeTitle)

    @commands.command(**T.ARCH.cmd.addGenre, ignore_extra=False)
    async def addGenre(self, ctx: commands.Context, *newGenre: str):
        async def changeGenre(story: Story):
            for genreName in newGenre:
                try:
                    story.addGenre(genreName.capitalize())
                    print(f"Added {genreName} genre to {story.cite()}.")
                except InvalidNameException:
                    await dmErrorAndRaise(ctx, T.ARCH.errorInvalidGenre(genreName))
                except DuplicateException:
                    await dmErrorAndRaise(ctx, T.ARCH.errorDupGenre(story.cite(), genreName))
        await self.setStoryAttr(ctx, changeGenre)
    
    @commands.command(**T.ARCH.cmd.removeGenre)
    async def removeGenre(self, ctx: commands.Context, *targetGenre: str):
        async def changeGenre(story: Story):
            for genreName in targetGenre:
                try:
                    story.removeGenre(genreName)
                    print(f"Removed {genreName} genre from {story.cite()}.")
                except NotFoundException:
                    await dmErrorAndRaise(ctx, T.ARCH.errorNoGenre(story.cite(), genreName))
        await self.setStoryAttr(ctx, changeGenre)
    
    @commands.command(**T.ARCH.cmd.setRating, ignore_extra=False)
    async def setRating(self, ctx: commands.Context, newRating: str):
        async def changeRating(story: Story):
            try:
                story.setRating(newRating)
                print(f"Set rating of {story.cite()} to {newRating}.")
            except InvalidNameException:
                await dmErrorAndRaise(ctx, T.ARCH.errorInvalidRating(story.cite(), newRating))
        await self.setStoryAttr(ctx, changeRating)
    
    @commands.command(**T.ARCH.cmd.setRatingReason)
    async def setratingreason(self, ctx: commands.Context, *newReason: str):
        newReason = " ".join(newReason)
        
        async def changeReason(story: Story):
            try:
                story.setRatingReason(newReason)
                print(f"Set rating reason of {story.cite()} to {newReason}.")
            except MaxLenException:
                await dmErrorAndRaise(ctx, T.ARCH.errorLenReason)
        await self.setStoryAttr(ctx, changeReason)

    @commands.command(**T.ARCH.cmd.addCharacter)
    async def addCharacter(self, ctx: commands.Context, *newCharacter: str):
        newCharName, newCharSpecies = await CogArchive.parseCharacter(ctx, " ".join(newCharacter))
        
        async def changeCharacter(story: Story):
            try:
                story.addCharacter(newCharSpecies, newCharName, ignoreMax=moderatorCheck(ctx))
                print(f"Added character with species {newCharSpecies} and name {newCharName} to {story.cite()}.")
            except DuplicateException:
                await dmErrorAndRaise(ctx, T.ARCH.errorDupChar(story.cite(), newCharSpecies, newCharName))
            except MaxSpeciesLenException:
                await dmErrorAndRaise(ctx, T.ARCH.errorLenCharSpecies)
            except MaxNameLenException:
                await dmErrorAndRaise(ctx, T.ARCH.errorLenCharName)
        await self.setStoryAttr(ctx, changeCharacter)
    
    @commands.command(**T.ARCH.cmd.removeCharacter)
    async def removeCharacter(self, ctx: commands.Context, *targetCharacter: str):
        targetCharName, targetCharSpecies = await CogArchive.parseCharacter(ctx, " ".join(targetCharacter))
        
        async def changeCharacter(story: Story):
            try:
                story.removeCharacter(targetCharSpecies, targetCharName)
                print(f"Removed character with species {targetCharSpecies} and name {targetCharName} from {story.cite()}.")
            except NotFoundException:
                await dmErrorAndRaise(ctx, T.ARCH.errorNoChar(story.cite(), targetCharSpecies, targetCharName))
        await self.setStoryAttr(ctx, changeCharacter)
    
    @commands.command(**T.ARCH.cmd.setSummary)
    async def setSummary(self, ctx: commands.Context, *newSummary: str):
        """ Sets the summary of the latest-added story of the issuer. """
        
        newSummary = " ".join(newSummary)
        
        async def changeSummary(story: Story):
            try:
                story.setSummary(newSummary, ignoreMax=moderatorCheck(ctx))
                print(f"Set summary of {story.cite()} to:\n{newSummary}")
            except MaxLenException:
                await dmErrorAndRaise(ctx, T.ARCH.errorLenSummary)
        await self.setStoryAttr(ctx, changeSummary)
    
    @commands.command(ignore_extra=False)
    async def addlink(self, ctx: commands.Context, linkSiteAbbr: str, linkURL: str):
        """ Adds a link with the given site abbreviation and URL to the latest-added story of the issuer.
            If targetTitle is specified, adds the link to that story instead. """
        
        async def changeLink(story: Story):
            try:
                story.addLink(linkSiteAbbr, linkURL, ignoreMax=moderatorCheck(ctx))
            except InvalidNameException:
                await dmErrorAndRaise(ctx, T.ARCH.errorInvalidLinkAbbr(story.cite(), linkSiteAbbr))
            except DuplicateException:
                await dmErrorAndRaise(ctx, T.ARCH.errorDupLink(story.cite(), linkSiteAbbr))
            except MaxLenException:
                await dmErrorAndRaise(ctx, T.ARCH.errorLenLinkURL)
        await self.setStoryAttr(ctx, changeLink)
    
    @commands.command(ignore_extra=False)
    async def removelink(self, ctx: commands.Context, targetSiteAbbr: str):
        """ Removes the link with the given name from the latest-added story of the issuer.
            If targetTitle is specified, removes the link from that story instead. """
        
        async def changeLink(story: Story):
            try:
                story.removeLink(targetSiteAbbr)
            except NotFoundException:
                await dmErrorAndRaise(ctx, T.ARCH.errorNoLink(story.cite(), targetSiteAbbr))
        await self.setStoryAttr(ctx, changeLink)
    
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
        await self.setStoryAttr(ctx, dummy)
