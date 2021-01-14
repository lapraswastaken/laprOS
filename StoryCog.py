
from typing import Callable, Optional
from discord.ext.commands.errors import CommandError
from discord.message import Message
from discord.ext.commands import Cog, command
from discord.ext.commands.context import Context
from discord.user import User
from discordUtils import dmError
import re
from Story import Character, Story

digitsPat = re.compile(r"(\d+)")
separator = "\n\n=====\n\n"
allRatings = ["K", "K+", "T", "M"]
allGenres = [
    "Adventure",
    "Angst",
    "Crime",
    "Drama",
    "Family",
    "Fantasy",
    "Friendship",
    "General",
    "Horror",
    "Humor",
    "Hurt/comfort",
    "Mystery",
    "Poetry",
    "Parody",
    "Romance",
    "Supernatural",
    "Suspense",
    "Sci-fi",
    "Spiritual",
    "Tragedy",
    "Western"
]
allLinkNames = [
    "AO3",
    "FFN",
    "RR",
    "DA",
    "WP"
]

class StoryCog(Cog):
    def __init__(self, bot, channelIDs: list[int]):
        self.bot = bot
        
        self.storyLinksChannelIDs = channelIDs
    
    async def cog_check(self, ctx: Context):
        if not ctx.channel.id in self.storyLinksChannelIDs:
            await ctx.send(content="This part of the bot can only be used in the channel that hosts story links.")
            return False
        return True
    
    async def cog_command_error(self, ctx: Context, error: CommandError):
        await dmError(ctx, str(error))
    
    async def getMessageForContext(self, ctx: Context) -> Optional[Message]:
        """ Gets the Message that mentions the Context's author. """
        
        foundMessage: Optional[Message] = None
        async for message in ctx.channel.history():
            if message.author.id != self.bot.user.id:
                continue
            if StoryCog.isMessageForAuthor(ctx.author, message):
                foundMessage = message
                break
        return foundMessage
    
    async def setStoryAttr(self, ctx: Context, targetTitle: Optional[str], changeCallback: Callable[[Story], None]):
        """ Finds the Story with the given title and performs the changeCallback on it. """
        
        foundMessage = await self.getMessageForContext(ctx)
        if not foundMessage:
            await dmError(ctx, "There are no story link posts created for you. Use .newstory to add a new story link post.")
            return
        
        stories = StoryCog.getStoriesFromMessage(foundMessage, ctx.author)
        
        targetStory = None
        if stories and not targetTitle:
            targetStory = stories[-1]
        else:
            for story in stories:
                if story.title == targetTitle:
                    targetStory = story
                    break
        if not targetStory:
            await dmError(ctx, f"Could not find a story you've created with the given name ({targetTitle}).")
            return
        
        await changeCallback(targetStory)
        
        await StoryCog.updateMessageWithStories(ctx.author, foundMessage, stories)
    
    @staticmethod
    def getStoriesFromMessage(message: Message, targetAuthor: User) -> list[Story]:
        """ Creates a list of stories from a message.
            Makes the author of all created stories the targetAuthor, confirmed with StoryCog.isMessageForAuthor. """
        
        storiesRaw = message.content.split(separator)[1:]
        
        stories: list[Story] = []
        for storyRaw in storiesRaw:
            story = Story.newFromText(targetAuthor, storyRaw)
            stories.append(story)
        return stories
        
    @staticmethod
    def isMessageForAuthor(author: User, message: Message):
        """ Checks to see if the given Message mentions the given author. """
        
        writerRaw = message.content.split(separator)[0]
        match = digitsPat.search(writerRaw)
        return match and int(match.group(1)) == author.id
    
    @staticmethod
    def allStoriesToText(author: User, stories: list[Story]):
        """ Creates the contents for a Message.
            Strings together the .toText() results of all Stories in the given list, prepending the author's mention tag. """
        
        return separator.join([f"**Writer**: {author.mention}"] + [story.toText() for story in stories])
    
    @staticmethod
    async def updateMessageWithStories(author: User, message: Message, stories: list[Story]):
        """ Updates a given Message's contents with the allStoriesToText method's result. """
        
        content = StoryCog.allStoriesToText(author, stories)
        await message.edit(content=content)
    
    @command(ignore_extra=False)
    async def newstory(self, ctx: Context, storyTitle: str):
        """ Adds a new story with the given title to the story links post for the command issuer.
            If no such post exist, creates one. 
            All other values except for title are left blank and must be altered with their respective .set commands. """
        
        foundMessage = await self.getMessageForContext(ctx)
        if not foundMessage:
            story = Story(storyTitle, ctx.author)
            await ctx.send(StoryCog.allStoriesToText(ctx.author, [story]))
            return
        
        stories = StoryCog.getStoriesFromMessage(foundMessage, ctx.author)
        stories.append(Story(storyTitle, ctx.author))
        await StoryCog.updateMessageWithStories(ctx.author, foundMessage, stories)
    
    @command(ignore_extra=False)
    async def settitle(self, ctx: Context, newTitle: str, targetTitle: str=None):
        """ Sets the title of the latest-added story of the issuer.
            if targetTitle is specified, sets the title of that story instead (this is somewhat unintuitive - the first parameter is still the new name of the story). """
            
        async def changeTitle(story: Story):
            story.title = newTitle
        await self.setStoryAttr(ctx, targetTitle, changeTitle)

    @command(ignore_extra=False)
    async def addgenre(self, ctx: Context, newGenre: str, targetTitle: str=None):
        """ Adds a genre to the latest-added story of the issuer.
            If targetTitle is specified, adds the genre to that story instead. """
        
        if not newGenre.capitalize() in allGenres:
            await dmError(ctx, f"The genre specified ({newGenre}) is not one of:\n\n" + "\n".join(allGenres))
            return
        
        async def changeGenre(story: Story):
            story.genres.append(newGenre.capitalize())
        await self.setStoryAttr(ctx, targetTitle, changeGenre)
    
    @command(ignore_extra=False)
    async def removegenre(self, ctx: Context, targetGenre: str, targetTitle: str=None):
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
                await dmError(ctx, f"That story does not have a genre called {targetGenre}")
        await self.setStoryAttr(ctx, targetTitle, changeGenre)
    
    @command(ignore_extra=False)
    async def setrating(self, ctx: Context, newRating: str, targetTitle: str=None):
        """ Sets the rating for the latest-added story of the issuer.
            If targetTitle is specified, sets the rating for that story instead. """
        
        if not newRating in allRatings:
            await dmError(ctx, f"The rating for your story must be one of {allRatings}, not {newRating}.")
            return
        
        async def changeRating(story: Story):
            story.rating = newRating
        await self.setStoryAttr(ctx, targetTitle, changeRating)
    
    @command(ignore_extra=False)
    async def setratingreason(self, ctx: Context, newReason: str, targetTitle: str=None):
        """ Sets the rating reason for the latest-added story of the issuer.
            If targetTitle is specified, sets the rating reason for that story instead. """
        
        def changeReason(story: Story):
            story.ratingReason = newReason
        await self.setStoryAttr(ctx, targetTitle, changeReason)

    @command(ignore_extra=False)
    async def addcharacter(self, ctx: Context, newCharName: str, charSpecies: str=None, targetTitle: str=None):
        """ Adds a character with the given name to the latest-added story of the issuer.
            A species can be given to the character with the charSpecies parameter. If this needs to be omitted so that a speciesless character can be added to a specific story, an empty string ("") can be passed.
            If targetTitle is specified, adds a character to that story instead. """
        
        newChar = Character(newCharName, charSpecies)
        
        async def changeCharacter(story: Story):
            story.characters.append(newChar)
        await self.setStoryAttr(ctx, targetTitle, changeCharacter)
    
    @command(ignore_extra=False)
    async def removecharacter(self, ctx: Context, targetCharName: str, targetTitle: str=None):
        """ Removes a character with the given name from the latest-added story of the issuer.
            If targetTitle is specified, removes a character from that story instead. """
        
        async def changeCharacter(story: Story):
            found = None
            for char in story.characters:
                if char.name == targetCharName:
                    found = char
            if found:
                story.characters.remove(found)
            else:
                await dmError(ctx, f"That story does not have a character named {targetCharName}.")
        await self.setStoryAttr(ctx, targetTitle, changeCharacter)
    
    @command(ignore_extra=False)
    async def setsummary(self, ctx: Context, newSummary: str, targetTitle: str=None):
        """ Sets the summary of the latest-added story of the issuer.
            If targetTitle is specified, sets the summary of that story instead. """
        
        async def changeSummary(story: Story):
            story.summary = newSummary
        await self.setStoryAttr(ctx, targetTitle, changeSummary)
    
    @command(ignore_extra=False)
    async def addlink(self, ctx: Context, newLinkName: str, link: str, targetTitle: str=None):
        """ Adds a link with the given name to the latest-added story of the issuer.
            If targetTitle is specified, adds the link to that story instead. """
        
        if not newLinkName in allLinkNames:
            await dmError(ctx, f"The rating for your story must be one of {allLinkNames}, not {newLinkName}.")
            return
        async def changeLink(story: Story):
            story.links[newLinkName] = link
        await self.setStoryAttr(ctx, targetTitle, changeLink)
    
    @command(ignore_extra=False)
    async def removelink(self, ctx: Context, targetLinkName: str, targetTitle: str=None):
        """ Removes the link with the given name from the latest-added story of the issuer.
            If targetTitle is specified, removes the link from that story instead. """
        
        async def changeLink(story: Story):
            if targetLinkName in story.links:
                story.links.pop(targetLinkName)
            else:
                await dmError(ctx, f"That story does not have a link with the name {targetLinkName}.")
        await self.setStoryAttr(ctx, targetTitle, changeLink)
