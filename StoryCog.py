
from Archive import ALL_GENRES, ALL_LINK_NAMES, ALL_RATINGS, DuplicateException, OVERARCH, Post
from typing import Union
import discord
from discord.ext import commands
from discordUtils import dmError, moderatorCheck
import re
from Archive import Character, Story

digitsPat = re.compile(r"(\d+)")
SEPARATOR = "\n\n=====\n\n"

class StoryCog(commands.Cog):
    def __init__(self):
        self.proxies: dict[int, discord.Member] = {}
    
    async def cog_check(self, ctx: commands.Context):
        if not OVERARCH.isValidChannelID(ctx.channel.id):
            await ctx.send(content="This part of the bot can only be used in the channel that hosts story links.")
            return False
        return True
    
    async def checkIsProxied(self, author: discord.Member) -> discord.Member:
        if not author.id in self.proxies:
            return author
        return await author.guild.fetch_member(self.proxies[author.id].id)
    
    @staticmethod
    async def updateArchivePost(archiveChannel: discord.TextChannel, post: Post):
        """ Updates the messages in a give archive text channel that make up a given post. """
        
        # fetch each message in the post's message ids
        messages: list[discord.Message] = []
        for messageID in post.messageIDs:
            try:
                messages.append(await archiveChannel.fetch_message(messageID))
            except discord.NotFound:
                post.messageIDs = []
                break
        
        if not messages:
            newMessage: discord.Message = await archiveChannel.send("*Hold on...*")
            messages.append(newMessage)
            post.messageIDs.append(newMessage.id)
        
        # begin to build the text to go into the first message
        postText = f"**Writer**: <@{post.authorID}>\n\n=====\n\n"
        for story in post.stories:
            # get the discord-formatted story text
            storyText = story.format()
            # if we can append the story text,
            if not len(storyText + postText) > 1800:
                # append the story text
                postText += storyText
            else:
                # otherwise, pop the earliest message off the list of the ones collected
                toEdit = messages.pop(0)
                # give it the content
                # if there are no remaining messages, we need to create a new one
                #  so that there is somewhere to put the remaining text after the loop
                if len(messages) == 0:
                    # create a new message
                    newMessage: discord.Message = await archiveChannel.send("*Hold on...*")
                    # add it to the list of messages
                    messages.append(newMessage)
                    # add it to the list of IDs
                    post.messageIDs.append(newMessage.id)
                postText += f"\n(Continued at <{messages[0].jump_url}>)"
                await toEdit.edit(content=postText)
                # give the jump link to the starting text for the next message
                postText = f"**Writer**: <@{post.authorID}>\n(Continued from <{toEdit.jump_url}>)\n\n=====\n\n" + storyText
        # add the remaining text to the last post in the messages
        await messages.pop(0).edit(content=postText)
        # if there are more messages after this one, delete them
        for remainingMessage in messages:
            await remainingMessage.delete()
        
    
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
    
    @commands.command(ignore_extra=False)
    #@commands.cooldown(1, 8 * 60, commands.BucketType.guild)
    async def addstory(self, ctx: commands.Context, storyTitle: str):
        """ Adds a new story with the given title to the story links post for the command issuer.
            If no such post exists, creates one. 
            All other values except for title are left blank and must be altered with their respective .set commands. """
        
        author = await self.checkIsProxied(ctx.author)
        archive = OVERARCH.getArchive(author.guild.id)
        if not archive:
            await dmError(ctx, "This server does not have an archive channel set up. Ask a server moderator to use the `setarchivechannel` command.")
            return
        post = archive.getPost(author.id)
        if not post:
            post = archive.createPost(author.id)
        
        newStory = Story(storyTitle)
        try:
            post.addStory(newStory)
        except DuplicateException:
            await dmError(ctx, "This command would create a story with a duplicate name!")
            return
        OVERARCH.write()
        await StoryCog.updateArchivePost(ctx.channel, post)
    
    @commands.command(ignore_extra=False)
    async def removestory(self, ctx: commands.Context, targetTitle: str):
        """ Removes the story with the given title. """
        
        foundMessage = await StoryCog.getMessageForAuthor(ctx)
        if not foundMessage:
            await dmError(ctx, "You haven't added any stories to remove!")
            return
        stories = await StoryCog.getStoriesFromMessage(foundMessage)
        
        found = None
        for story in stories:
            if story.title == targetTitle:
                found = story
                break
        if not found:
            await dmError(ctx, f"Couldn't find a story to remove with the name {targetTitle}.")
        stories.remove(found)
        await self.updateMessageWithStories(ctx.author, foundMessage, stories)
    
    @commands.command(ignore_extra=False)
    async def settitle(self, ctx: commands.Context, newTitle: str, targetTitle: str=None):
        """ Sets the title of the latest-added story of the issuer.
            if targetTitle is specified, sets the title of that story instead (this is somewhat unintuitive - the first parameter is still the new name of the story). """
            
        async def changeTitle(story: Story):
            story.title = newTitle
        await self.setStoryAttr(ctx, targetTitle, changeTitle)

    @commands.command(ignore_extra=False)
    async def addgenre(self, ctx: commands.Context, newGenre: str, targetTitle: str=None):
        """ Adds a genre to the latest-added story of the issuer.
            If targetTitle is specified, adds the genre to that story instead. """
        
        if not newGenre.capitalize() in ALL_GENRES:
            await dmError(ctx, f"The genre specified ({newGenre}) is not one of the following:\n\n" + "\n".join(ALL_GENRES))
            return
        
        async def changeGenre(story: Story):
            if newGenre in story.genres:
                return
            story.genres.append(newGenre.capitalize())
        await self.setStoryAttr(ctx, targetTitle, changeGenre)
    
    @commands.command(ignore_extra=False)
    async def removegenre(self, ctx: commands.Context, targetGenre: str, targetTitle: str=None):
        """ Removes the specified genre from the latest-added story of the issuer.
            If targetTitle is specified, removes the genre from that story instead. """
        
        async def changeGenre(story: Story):
            found = None
            for genre in story.genres:
                if genre == targetGenre:
                    found = genre
            if found:
                story.genres.remove(found)
            else:
                await dmError(ctx, f"The story \"{story.title}\" does not have a genre called {targetGenre}.")
        await self.setStoryAttr(ctx, targetTitle, changeGenre)
    
    @commands.command(ignore_extra=False)
    async def setrating(self, ctx: commands.Context, newRating: str, targetTitle: str=None):
        """ Sets the rating for the latest-added story of the issuer.
            If targetTitle is specified, sets the rating for that story instead. """
        
        if not newRating in ALL_RATINGS:
            await dmError(ctx, f"The rating for your story must be one of {ALL_RATINGS}, not {newRating}.")
            return
        
        async def changeRating(story: Story):
            story.rating = newRating
        await self.setStoryAttr(ctx, targetTitle, changeRating)
    
    @commands.command(ignore_extra=False)
    async def setratingreason(self, ctx: commands.Context, newReason: str, targetTitle: str=None):
        """ Sets the rating reason for the latest-added story of the issuer.
            If targetTitle is specified, sets the rating reason for that story instead. """
        
        async def changeReason(story: Story):
            story.ratingReason = newReason
        await self.setStoryAttr(ctx, targetTitle, changeReason)

    @commands.command(ignore_extra=False)
    async def addcharacter(self, ctx: commands.Context, newCharSpecies: str, newCharNickname: str="", targetTitle: str=None):
        """ Adds a character with the given species and optional nickname to the latest-added story of the issuer.
            A species can be given to the character with the charSpecies parameter. If this needs to be omitted so that a speciesless character can be added to a specific story, an empty string ("") can be passed.
            If targetTitle is specified, adds a character to that story instead. """
        
        newChar = Character(newCharSpecies, newCharNickname)
        if "|" in newCharNickname + newCharSpecies:
            await dmError(ctx, "You cant use vertical bars in the species name or the nickname when adding a new character.")
            return
        
        async def changeCharacter(story: Story):
            story.characters.append(newChar)
        await self.setStoryAttr(ctx, targetTitle, changeCharacter)
    
    @commands.command(ignore_extra=False)
    async def removecharacter(self, ctx: commands.Context, targetCharSpecies: str, targetTitle: str=None):
        """ Removes a character with the given species from the latest-added story of the issuer.
            If targetTitle is specified, removes a character from that story instead. """
        
        async def changeCharacter(story: Story):
            found = None
            for char in story.characters:
                if char.species == targetCharSpecies:
                    found = char
            if found:
                story.characters.remove(found)
            else:
                await dmError(ctx, f"The story \"{story.title}\" does not have a character with the species {targetCharSpecies}.")
        await self.setStoryAttr(ctx, targetTitle, changeCharacter)
    
    @commands.command(ignore_extra=False)
    async def setsummary(self, ctx: commands.Context, newSummary: str, targetTitle: str=None):
        """ Sets the summary of the latest-added story of the issuer.
            If targetTitle is specified, sets the summary of that story instead. """
        
        if "```" in newSummary:
            await dmError(ctx, "You can't use \"```\" in your summary.")
        
        async def changeSummary(story: Story):
            story.summary = newSummary
        await self.setStoryAttr(ctx, targetTitle, changeSummary)
    
    @commands.command(ignore_extra=False)
    async def addlink(self, ctx: commands.Context, linkCategory: str, linkURL: str, targetTitle: str=None):
        """ Adds a link with the given name to the latest-added story of the issuer.
            If targetTitle is specified, adds the link to that story instead. """
        
        if not linkCategory in ALL_LINK_NAMES:
            await dmError(ctx, f"The link name for your story must be one of {ALL_LINK_NAMES.values()}, not {linkCategory}.")
            return
        async def changeLink(story: Story):
            story.links[linkCategory] = linkURL
        await self.setStoryAttr(ctx, targetTitle, changeLink)
    
    @commands.command(ignore_extra=False)
    async def removelink(self, ctx: commands.Context, targetLinkName: str, targetTitle: str=None):
        """ Removes the link with the given name from the latest-added story of the issuer.
            If targetTitle is specified, removes the link from that story instead. """
        
        async def changeLink(story: Story):
            if targetLinkName in story.links:
                story.links.pop(targetLinkName)
            else:
                await dmError(ctx, f"The story \"{story.title}\" does not have a link with the name {targetLinkName}.")
        await self.setStoryAttr(ctx, targetTitle, changeLink)
