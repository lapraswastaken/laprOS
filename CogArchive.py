
from discord.channel import DMChannel
from Story import getStoriesFromMessage
from typing import Callable, Optional, Union
import discord
from discord.ext import commands
from discordUtils import dm, fail, getEmbed, getStringArgsFromText, moderatorCheck
import re
from Archive import Archive, Story, DuplicateException, InvalidNameException, MaxLenException, MaxNameLenException, MaxSpeciesLenException, NotFoundException, OVERARCH, Post
import sources.text as T
from sources.general import BOT_PREFIX

A = T.ARCH

reactionLockedMessageIDs: list[int] = []

class CogArchive(commands.Cog, **A.cog):
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
        self.proxies: dict[int, discord.Member] = {}
        self.dmPosts: dict[int, discord.Message] = {}
    
    async def cog_check(self, ctx: commands.Context):
        if isinstance(ctx.channel, discord.DMChannel):
            return True
        if not OVERARCH.isValidChannelID(ctx.channel.id):
            await ctx.send(content=A.errorNotInArchiveChannel)
            return False
        return True
    
    async def checkIsMemberProxied(self, author: discord.Member) -> discord.Member:
        if not author.id in self.proxies:
            return author
        return await author.guild.fetch_member(self.proxies[author.id].id)
    
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
        if not payload.guild_id:
            if payload.message_id in self.dmPosts:
                payload.guild_id = self.dmPosts[payload.message_id].channel.guild.id
            else:
                return
        archive = OVERARCH.getArchive(payload.guild_id)
        if (not archive) or (not payload.member) or (payload.member.bot): return
        
        archiveChannel: discord.TextChannel = payload.member.guild.get_channel(payload.channel_id)
        message: discord.Message = await archiveChannel.fetch_message(payload.message_id)
        
        try:
            post = archive.getPostByMessageID(payload.message_id)
        except NotFoundException:
            return
        
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
    
    @staticmethod
    async def getArchive(ctx: commands.Context) -> Archive:
        """ Gets the Archive object associated with a context's guild. """
        if isinstance(ctx.channel, discord.DMChannel):
            try:
                archive = OVERARCH.getArchiveForUser(ctx.author.id)
            except NotFoundException:
                fail(T.RETR.errorNoArchivePreference)
        else:
            archive = OVERARCH.getArchive(ctx.guild.id)
        if not archive:
            fail(A.errorNoArchiveChannel)
        return archive
        
    async def updateArchivePost(self, archiveChannel: discord.TextChannel, post: Post, story: Optional[Story]):
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
            message: discord.Message = await archiveChannel.send(A.archivePostMessageWait)
            await message.add_reaction(T.UTIL.emojiFirst)
            await message.add_reaction(T.UTIL.emojiPrior)
            await message.add_reaction(T.UTIL.emojiNext)
            await message.add_reaction(T.UTIL.emojiLast)
            post.messageID = message.id
        
        post.focusStory(story)
        await self.updateFocusedStory(message, post)
    
    async def getPostAuthorArchive(self, ctx: commands.Context, error: bool=True) -> tuple[Post, discord.User, Archive]:
        """ Gets the post, the author, and the archive from the context. If `error`, if a post isn't found, the context is notified and an error is thrown. """
        
        author = await self.checkIsMemberProxied(ctx.author)
        archive = await CogArchive.getArchive(ctx)
        post = archive.getPost(author.id)
        if error and not post:
            fail(A.errorNoPost)
        return post, author, archive
    
    async def setStoryAttr(self, ctx: commands.Context, changer: Callable[[Story], None]=None):
        """ Calls the `changer` function on the currently focused story in the post linked to the context. """
        
        post, _, archive = await self.getPostAuthorArchive(ctx)

        story = post.getFocusedStory()
        
        if changer:
            await changer(story)
        
        guild: discord.Guild = await self.bot.fetch_guild(archive.guildID)
        channel: discord.TextChannel = discord.utils.get(await guild.fetch_channels(), id=archive.channelID)
        if not channel:
            fail(A.errorNoArchiveChannel)
        await self.updateArchivePost(channel, post, story)
        OVERARCH.write()
    
    @commands.command(**A.proxyUser.meta, ignore_extra=False, hidden=True)
    @commands.check(moderatorCheck)
    async def proxyUser(self, ctx: commands.Context, member: Union[discord.Member, int]):
        if isinstance(member, int):
            member = await ctx.guild.get_member(member)
        self.proxies[ctx.author.id] = member
        await dm(ctx, A.proxyUser.success(member.id))
    
    @commands.command(**A.clearProxy.meta, ignore_extra=False, hidden=True)
    @commands.check(moderatorCheck)
    async def clearProxy(self, ctx: commands.Context):
        if ctx.author.id in self.proxies:
            id = self.proxies.pop(ctx.author.id)
            await dm(ctx, A.clearProxy.success(id))
        else:
            await dm(ctx, A.clearProxy.noProxy)
    
    @commands.command(**A.focus.meta)
    async def focus(self, ctx: commands.Context, *, targetStory: str):
        post, *_ = await self.getPostAuthorArchive(ctx)
        try:
            post.focusStoryByName(targetStory)
        except NotFoundException:
            fail(A.focus.errorNotFound(targetStory))
        await self.setStoryAttr(ctx)
        
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
                    except TypeError as e:
                        await fail(A.multi.errorArgs(targetCmdName))
                    break
            
            if not found:
                fail(A.multi.errorInvalid(targetCmdName))
    
    @commands.command(**A.getMyPost.meta)
    async def getMyPost(self, ctx: commands.Context):
        if not isinstance(ctx.channel, discord.DMChannel):
            fail(A.getMyPost.errorNoDM)
        post, _, archive = await self.getPostAuthorArchive(ctx)
        guildID = OVERARCH.getGuildIDFromArchive(archive)
        
        message: discord.Message = await ctx.send(A.archivePostMessageWait)
        self.dmPosts[post.messageID] = message
        await self.updateFocusedStory(message, post)
        
            
    @commands.command(**A.addStory.meta)
    @commands.cooldown(1, 8 * 60, commands.BucketType.guild)
    async def addStory(self, ctx: commands.Context, *storyTitle: str):
        # not kwarg so it works with multi
        storyTitle = " ".join(storyTitle)
        
        post, author, archive = await self.getPostAuthorArchive(ctx, False)
        if not post:
            post = archive.createPost(author.id)
        
        try:
            newStory = Story(storyTitle)
            post.addStory(newStory)
        except MaxLenException:
            fail(A.addStory.errorLen(len(storyTitle))); return
        except DuplicateException:
            fail(A.addStory.errorDup(storyTitle)); return
        await self.setStoryAttr(ctx)
        OVERARCH.write()
    
    @commands.command(**A.removeStory.meta)
    async def removeStory(self, ctx: commands.Context, *targetTitle: str):
        targetTitle = " ".join(targetTitle)
        post, *_ = await self.getPostAuthorArchive(ctx)
        
        try:
            post.removeStory(targetTitle)
        except NotFoundException:
            fail(A.removeStory.errorNotFound(targetTitle))
            
        await self.setStoryAttr(ctx)
        OVERARCH.write()
    
    @commands.command(**A.setTitle.meta)
    async def setTitle(self, ctx: commands.Context, *newTitle: str):
        newTitle = " ".join(newTitle)
            
        async def changeTitle(story: Story):
            try:
                story.setTitle(newTitle)
            except MaxLenException:
                fail(A.setTitle.errorLen(len(newTitle)))
        await self.setStoryAttr(ctx, changeTitle)

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
        await self.setStoryAttr(ctx, changeGenre)
    
    @commands.command(**A.removeGenre.meta)
    async def removeGenre(self, ctx: commands.Context, *targetGenre: str):
        async def changeGenre(story: Story):
            for genreName in targetGenre:
                try:
                    story.removeGenre(genreName)
                    print(f"Removed {genreName} genre from {story.cite()}.")
                except NotFoundException:
                    fail(A.removeGenre.errorNotFound(story.cite(), genreName))
        await self.setStoryAttr(ctx, changeGenre)
    
    @commands.command(**A.setRating.meta, ignore_extra=False)
    async def setRating(self, ctx: commands.Context, newRating: str):
        async def changeRating(story: Story):
            try:
                story.setRating(newRating)
                print(f"Set rating of {story.cite()} to {newRating}.")
            except InvalidNameException:
                fail(A.setRating.errorInvalid(story.cite(), newRating))
        await self.setStoryAttr(ctx, changeRating)
    
    @commands.command(**A.setRatingReason.meta)
    async def setratingreason(self, ctx: commands.Context, *newReason: str):
        newReason = " ".join(newReason)
        
        async def changeReason(story: Story):
            try:
                story.setRatingReason(newReason)
                print(f"Set rating reason of {story.cite()} to {newReason}.")
            except MaxLenException:
                fail(A.setRatingReason.errorLen(newReason))
        await self.setStoryAttr(ctx, changeReason)

    @commands.command(**A.addCharacter.meta)
    async def addCharacter(self, ctx: commands.Context, *newCharacter: str):
        newCharName, newCharSpecies = await CogArchive.parseCharacter(ctx, " ".join(newCharacter))
        
        async def changeCharacter(story: Story):
            try:
                story.addCharacter(newCharSpecies, newCharName, ignoreMax=moderatorCheck(ctx))
                print(f"Added character with species {newCharSpecies} and name {newCharName} to {story.cite()}.")
            except DuplicateException:
                fail(A.addCharacter.errorDup(story.cite(), newCharSpecies, newCharName))
            except MaxSpeciesLenException:
                fail(A.addCharacter.errorLenSpecies(len(newCharSpecies)))
            except MaxNameLenException:
                fail(A.addCharacter.errorLenName(len(newCharName)))
        await self.setStoryAttr(ctx, changeCharacter)
    
    @commands.command(**A.removeCharacter.meta)
    async def removeCharacter(self, ctx: commands.Context, *targetCharacter: str):
        targetCharName, targetCharSpecies = await CogArchive.parseCharacter(ctx, " ".join(targetCharacter))
        
        async def changeCharacter(story: Story):
            try:
                story.removeCharacter(targetCharSpecies, targetCharName)
                print(f"Removed character with species {targetCharSpecies} and name {targetCharName} from {story.cite()}.")
            except NotFoundException:
                fail(A.removeCharacter.errorNorFound(story.cite(), targetCharSpecies, targetCharName))
        await self.setStoryAttr(ctx, changeCharacter)
    
    @commands.command(**A.setSummary.meta)
    async def setSummary(self, ctx: commands.Context, *newSummary: str):
        
        newSummary = " ".join(newSummary)
        
        async def changeSummary(story: Story):
            try:
                story.setSummary(newSummary, ignoreMax=moderatorCheck(ctx))
                print(f"Set summary of {story.cite()} to:\n{newSummary}")
            except MaxLenException:
                fail(A.setSummary.errorLen(len(newSummary)))
        await self.setStoryAttr(ctx, changeSummary)
    
    @commands.command(**A.addLink.meta, ignore_extra=False)
    async def addlink(self, ctx: commands.Context, linkSiteAbbr: str, linkURL: str):
        
        async def changeLink(story: Story):
            try:
                story.addLink(linkSiteAbbr, linkURL, ignoreMax=moderatorCheck(ctx))
            except InvalidNameException:
                fail(A.addLink.errorInvalid(story.cite(), linkSiteAbbr))
            except DuplicateException:
                fail(A.addLink.errorDup(story.cite(), linkSiteAbbr))
            except MaxLenException:
                fail(A.addLink.errorLen(len(linkURL)))
        await self.setStoryAttr(ctx, changeLink)
    
    @commands.command(**A.removeLink.meta, ignore_extra=False)
    async def removelink(self, ctx: commands.Context, targetSiteAbbr: str):
        
        async def changeLink(story: Story):
            try:
                story.removeLink(targetSiteAbbr)
            except NotFoundException:
                fail(A.removeLink.errorNotFound(story.cite(), targetSiteAbbr))
        await self.setStoryAttr(ctx, changeLink)
    
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
            await self.setStoryAttr(ctx)

    @commands.command(**A.refreshPost.meta, hidden=True)
    @commands.check(moderatorCheck)
    async def refreshPost(self, ctx: commands.Context):
        async def dummy(_): pass
        await self.setStoryAttr(ctx, dummy)
