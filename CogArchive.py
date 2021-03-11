
import discord
from discord.ext import commands
from typing import Callable, Optional, Union
import time

from Archive import Story, DuplicateException, InvalidNameException, MaxLenException, MaxNameLenException, MaxSpeciesLenException, NotFoundException, OVERARCH, Post
from discordUtils import fail, fetchChannel, getArchiveFromContext, getAuthorFromContext, getEmbed, getStringArgsFromText, canHandleArchive, isModerator, laprOSException, moderatorCheck
import sources.text as T
from sources.general import BOT_PREFIX
from Story import getStoriesFromMessage

A = T.ARCH

reactionLockedMessageIDs: list[int] = []

class CogArchive(commands.Cog, **A.cog):
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
        self.proxies: dict[int, discord.Member] = {}
        self.dmPosts: dict[int, discord.Message] = {}
        self.addStoryCooldown = 0
    
    async def cog_check(self, ctx: commands.Context):
        inCorrectChannel = canHandleArchive(ctx)
        if not inCorrectChannel:
            await ctx.send(content=T.UTIL.errorNotInArchiveChannel)
            return False
        
        if not ctx.author.id in OVERARCH.userArchivePrefs:
            OVERARCH.setArchivePref(ctx.author.id, ctx.guild.id)
            OVERARCH.write()
        return True
    
    @staticmethod
    async def parseCharacter(ctx: commands.Context, text: str) -> tuple[str, str]:
        """ Gets the character name (optional, may be empty string) and the character species from a string. """
        parts = [part.strip() for part in text.split(",", 1)]
        if not parts[0]:
            fail(A.errorParseCharacterNoSpecies)
        if len(parts) == 2:
            return parts[0], " ".join([word.capitalize() for word in parts[1].split(" ")])
        else:
            return "", " ".join([word.capitalize() for word in parts[0].split(" ")])
    
    async def handleReactionAdd(self, payload: discord.RawReactionActionEvent):
        if payload.message_id in reactionLockedMessageIDs: return
        if payload.member and payload.member.bot: return
        
        if payload.guild_id:
            archive = OVERARCH.getArchiveForGuild(payload.guild_id)
        else:
            archive = OVERARCH.getArchiveForUser(payload.user_id)
        if not archive: return
        try:
            post = archive.getPostByMessageID(payload.message_id)
        except NotFoundException:
            return
        
        guild = await self.bot.fetch_guild(archive.guildID)
        
        archiveChannel: discord.TextChannel = await fetchChannel(guild, archive.channelID)
        message: discord.Message = await archiveChannel.fetch_message(post.messageID)
        
        emoji = str(payload.emoji)
        
        if emoji == T.UTIL.emojiFirst:
            post.focused = 0
        elif emoji == T.UTIL.emojiPrior and post.focused > 0:
            post.focused -= 1
        elif emoji == T.UTIL.emojiNext and post.focused < len(post.stories) - 1:
            post.focused += 1
        elif emoji == T.UTIL.emojiLast:
            post.focused = len(post.stories) - 1
        
        await self.updateFocusedStory(message, post)
        
    async def updateFocusedStory(self, message: discord.Message, post: Post):
        """ Edits the message with the formatted contents of the post and refreshes its pagination reactions. """
        
        if message.id in self.dmPosts:
            await self.updateFocusedStory(self.dmPosts[message.id], post)
        reactionLockedMessageIDs.append(message.id)
        
        story = post.getFocusedStory()
        if not story:
            await message.delete()
            return
        if len(post.stories) > 1:
            await message.edit(
                content=A.archivePostMessageBody(post.authorID, story.format()[:1800]),
                embed=getEmbed(**A.archivePostEmbed(post.format()))
            )
        else:
            await message.edit(
                content=A.archivePostMessageBody(post.authorID, story.format()[:1800]),
                embed=None
            )
        
        if not isinstance(message.channel, discord.DMChannel):
            await message.clear_reactions()
            if post.focused > 0:
                if len(post.stories) > 2:
                    await message.add_reaction(T.UTIL.emojiFirst)
                await message.add_reaction(T.UTIL.emojiPrior)
            if post.focused < len(post.stories) - 1:
                await message.add_reaction(T.UTIL.emojiNext)
                if len(post.stories) > 2:
                    await message.add_reaction(T.UTIL.emojiLast)
        
        reactionLockedMessageIDs.remove(message.id)
    
    async def getPost(self, ctx: commands.Context):
        """ Gets the post from the context. If `error`, if a post isn't found, the context is notified and an error is thrown. """
        
        archive = getArchiveFromContext(ctx)
        author = await getAuthorFromContext(ctx)
        post = archive.getPost(author.id)
        if not post:
            fail(A.errorNoPost)
        return post
    
    async def updatePost(self, ctx: commands.Context, changer: Callable[[Story], None]=None):
        """ Calls the `changer` function on the currently focused story in the post linked to the context. """
        
        post = await self.getPost(ctx)
        story = post.getFocusedStory()
        
        guild: discord.Guild = await self.bot.fetch_guild(post.archive.guildID)
        archiveChannel: discord.TextChannel = discord.utils.get(await guild.fetch_channels(), id=post.archive.channelID)
        if not archiveChannel:
            fail(A.errorNoArchiveChannel)
        
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
                post.delete()
                return
            # this shouldn't happen
            else:
                fail("Deleted a story for a post with a nonexistent message ID. How does that work...?")
        
        if changer:
            await changer(story)
        
        try:
            message = await archiveChannel.fetch_message(post.messageID)
        except (discord.NotFound, discord.HTTPException):
            message: discord.Message = await archiveChannel.send(A.archivePostMessageWait)
            await message.add_reaction(T.UTIL.emojiFirst)
            await message.add_reaction(T.UTIL.emojiPrior)
            await message.add_reaction(T.UTIL.emojiNext)
            await message.add_reaction(T.UTIL.emojiLast)
            post.messageID = message.id
        
        await self.updateFocusedStory(message, post)
        OVERARCH.write()
    
    @commands.command(**A.focus.meta)
    async def focus(self, ctx: commands.Context, *, targetStory: Union[int, str]):
        post = await self.getPost(ctx)
        if isinstance(targetStory, int):
            targetStory -= 1
            try:
                post.focusByIndex(targetStory)
            except MaxLenException:
                fail(A.focus.errorIndex(targetStory))
        else:
            try:
                post.focusByTitle(targetStory.lower())
            except NotFoundException:
                fail(A.focus.errorNotFound(targetStory))
        await self.updatePost(ctx)
        
    @commands.command(**A.multi.meta)
    async def multi(self, ctx: commands.Context, *, allTextCommands: str):
        # thank you, love
        
        allTextCommands = [command if not command.startswith(BOT_PREFIX) else command[len(BOT_PREFIX):] for command in allTextCommands.split("\n")]
        
        for textCommand in allTextCommands:
            targetCmdName: str = None
            args: list[str] = None
            try:
                targetCmdName, *args = getStringArgsFromText(textCommand)
            except SyntaxError:
                fail(A.multi.errorQuotes(textCommand))
            
            commandFn: commands.Command
            found = False
            for commandFn in self.get_commands():
                if targetCmdName.lower() == commandFn.name or targetCmdName.lower() in commandFn.aliases:
                    try:
                        print(f"running command {targetCmdName}")
                        await commandFn(ctx, *args)
                        found = True
                    except TypeError:
                        await fail(A.multi.errorArgs(targetCmdName))
                    break
            
            if not found:
                fail(A.multi.errorInvalid(targetCmdName))
    
    @commands.command(**A.getMyPost.meta)
    async def getMyPost(self, ctx: commands.Context):
        if not isinstance(ctx.channel, discord.DMChannel):
            fail(A.getMyPost.errorNoDM)
        post = await self.getPost(ctx)
        
        message: discord.Message = await ctx.send(A.archivePostMessageWait)
        self.dmPosts[post.messageID] = message
        await self.updateFocusedStory(message, post)
        
            
    @commands.command(**A.addStory.meta)
    async def addStory(self, ctx: commands.Context, *storyTitle: str):
        # not kwarg so it works with multi
        storyTitle = " ".join(storyTitle)
        author = await getAuthorFromContext(ctx)
        
        now = time.time()
        isNewPost = False
        try:
            post = await self.getPost(ctx)
        except laprOSException:
            print("Creating new post.")
            archive = getArchiveFromContext(ctx)
            post = archive.createPost(author.id)
        
            last = self.addStoryCooldown
            diff = now - last
            print(diff)
            diff = (60 * 10) - diff
            if diff > 0:
                mins = round(diff / 60, 2)
                fail(A.addStory.errorCooldown(mins))
            isNewPost = True
        
        try:
            newStory = Story()
            newStory.setTitle(storyTitle, ignoreMax=isModerator(ctx.author))
            post.addStory(newStory)
            post.focusByTitle(newStory.title)
        except MaxLenException:
            fail(A.addStory.errorLen(len(storyTitle))); return
        except DuplicateException:
            fail(A.addStory.errorDup(storyTitle)); return
        await self.updatePost(ctx)
        if isinstance(ctx.channel, discord.DMChannel):
            if not post.messageID in self.dmPosts:
                await self.getMyPost(ctx)
        
        if isNewPost:
            self.addStoryCooldown = now
    
    @commands.command(**A.removeStory.meta)
    async def removeStory(self, ctx: commands.Context, *targetTitle: str):
        targetTitle = " ".join(targetTitle)
        post = await self.getPost(ctx)
        
        try:
            post.removeStory(targetTitle)
        except NotFoundException:
            fail(A.removeStory.errorNotFound(targetTitle))
            
        await self.updatePost(ctx)
    
    @commands.command(**A.setTitle.meta)
    async def setTitle(self, ctx: commands.Context, *newTitle: str):
        
        newTitle = " ".join(newTitle)
        author = await getAuthorFromContext(ctx)
            
        async def changeTitle(story: Story):
            try:
                story.setTitle(newTitle, ignoreMax=isModerator(ctx.author))
            except MaxLenException:
                fail(A.setTitle.errorLen(len(newTitle)))
        await self.updatePost(ctx, changeTitle)

    @commands.command(**A.addGenre.meta)
    async def addGenre(self, ctx: commands.Context, *newGenre: str):
        async def changeGenre(story: Story):
            for genreName in newGenre:
                try:
                    story.addGenre(genreName.capitalize())
                    print(f"Added {genreName} genre to {story.cite()}.")
                except InvalidNameException:
                    fail(A.addGenre.errorInvalid(genreName))
                except DuplicateException:
                    fail(A.addGenre.errorDup(story.cite(), genreName))
        await self.updatePost(ctx, changeGenre)
    
    @commands.command(**A.removeGenre.meta)
    async def removeGenre(self, ctx: commands.Context, *targetGenre: str):
        async def changeGenre(story: Story):
            for genreName in targetGenre:
                try:
                    story.removeGenre(genreName)
                    print(f"Removed {genreName} genre from {story.cite()}.")
                except NotFoundException:
                    fail(A.removeGenre.errorNotFound(story.cite(), genreName))
        await self.updatePost(ctx, changeGenre)
    
    @commands.command(**A.setRating.meta, ignore_extra=False)
    async def setRating(self, ctx: commands.Context, newRating: str):
        newRating = newRating.upper()
        
        async def changeRating(story: Story):
            try:
                story.setRating(newRating)
                print(f"Set rating of {story.cite()} to {newRating}.")
            except InvalidNameException:
                fail(A.setRating.errorInvalid(story.cite(), newRating))
        await self.updatePost(ctx, changeRating)
    
    @commands.command(**A.setRatingReason.meta)
    async def setratingreason(self, ctx: commands.Context, *newReason: str):
        newReason = " ".join(newReason)
        author = await getAuthorFromContext(ctx)
        
        async def changeReason(story: Story):
            try:
                story.setRatingReason(newReason, ignoreMax=isModerator(ctx.author))
                print(f"Set rating reason of {story.cite()} to {newReason}.")
            except MaxLenException:
                fail(A.setRatingReason.errorLen(newReason))
        await self.updatePost(ctx, changeReason)

    @commands.command(**A.addCharacter.meta)
    async def addCharacter(self, ctx: commands.Context, *newCharacter: str):
        
        newCharName, newCharSpecies = await CogArchive.parseCharacter(ctx, " ".join(newCharacter))
        author = await getAuthorFromContext(ctx)
        
        async def changeCharacter(story: Story):
            try:
                story.addCharacter(newCharSpecies, newCharName, ignoreMax=isModerator(ctx.author))
                print(f"Added character with species {newCharSpecies} and name {newCharName} to {story.cite()}.")
            except DuplicateException:
                fail(A.addCharacter.errorDup(story.cite(), newCharSpecies, newCharName))
            except MaxSpeciesLenException:
                fail(A.addCharacter.errorLenSpecies(len(newCharSpecies)))
            except MaxNameLenException:
                fail(A.addCharacter.errorLenName(len(newCharName)))
        await self.updatePost(ctx, changeCharacter)
    
    @commands.command(**A.removeCharacter.meta)
    async def removeCharacter(self, ctx: commands.Context, *targetCharacter: str):
        targetCharName, targetCharSpecies = await CogArchive.parseCharacter(ctx, " ".join(targetCharacter))
        
        async def changeCharacter(story: Story):
            try:
                story.removeCharacter(targetCharSpecies, targetCharName)
                print(f"Removed character with species {targetCharSpecies} and name {targetCharName} from {story.cite()}.")
            except NotFoundException:
                fail(A.removeCharacter.errorNorFound(story.cite(), targetCharSpecies, targetCharName))
        await self.updatePost(ctx, changeCharacter)
    
    @commands.command(**A.setSummary.meta)
    async def setSummary(self, ctx: commands.Context, *newSummary: str):
        
        newSummary = " ".join(newSummary)
        author = await getAuthorFromContext(ctx)
        
        async def changeSummary(story: Story):
            try:
                story.setSummary(newSummary, ignoreMax=isModerator(ctx.author))
                print(f"Set summary of {story.cite()} to:\n{newSummary}")
            except MaxLenException:
                fail(A.setSummary.errorLen(len(newSummary)))
        await self.updatePost(ctx, changeSummary)
    
    @commands.command(**A.addLink.meta, ignore_extra=False)
    async def addlink(self, ctx: commands.Context, linkSiteAbbr: str, linkURL: str):
        
        linkSiteAbbr = linkSiteAbbr.upper()
        author = await getAuthorFromContext(ctx)
        
        async def changeLink(story: Story):
            try:
                story.addLink(linkSiteAbbr, linkURL, ignoreMax=isModerator(ctx.author))
            except InvalidNameException:
                fail(A.addLink.errorInvalid(story.cite(), linkSiteAbbr))
            except DuplicateException:
                fail(A.addLink.errorDup(story.cite(), linkSiteAbbr))
            except MaxLenException:
                fail(A.addLink.errorLen(len(linkURL)))
        await self.updatePost(ctx, changeLink)
    
    @commands.command(**A.removeLink.meta, ignore_extra=False)
    async def removelink(self, ctx: commands.Context, targetSiteAbbr: str):
        
        async def changeLink(story: Story):
            try:
                story.removeLink(targetSiteAbbr)
            except NotFoundException:
                fail(A.removeLink.errorNotFound(story.cite(), targetSiteAbbr))
        await self.updatePost(ctx, changeLink)
    
    @commands.command(**A.convert.meta, hidden=True)
    @commands.check(moderatorCheck)
    async def convert(self, ctx: commands.Context, limit: int=None):
        
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
            await self.updatePost(ctx)

    @commands.command(**A.refreshPost.meta, hidden=True)
    @commands.check(moderatorCheck)
    async def refreshPost(self, ctx: commands.Context):
        async def dummy(_): pass
        await self.updatePost(ctx, dummy)
        self.addStoryCooldown = time.time()
