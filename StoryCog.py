
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
    "General",
    "Romance",
    "Humor",
    "Drama",
    "Poetry",
    "Adventure",
    "Mystery",
    "Horror",
    "Parody",
    "Angst",
    "Supernatural",
    "Suspense",
    "Sci-fi",
    "Fantasy",
    "Spiritual",
    "Tragedy",
    "Western",
    "Crime",
    "Family",
    "Hurt/Comfort"
]

class StoryCog(Cog):
    def __init__(self, bot, channelIDs: list[int]):
        self.bot = bot
        
        self.storyLinksChannelIDs = channelIDs
    
    async def cog_check(self, ctx: Context):
        if ctx.command.name == "help":
            return True
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
    
    async def setStoryAttr(self, ctx: Context, targetTitle: str, changeCallback: Callable[[Story], None]):
        """ Finds the Story with the given title and performs the changeCallback on it. """
        
        foundMessage = await self.getMessageForContext(ctx)
        if not foundMessage:
            await dmError(ctx, "There are no story link posts created for you. Use .newstory to add a new story link post.")
            return
        
        stories = StoryCog.getStoriesFromMessage(foundMessage, ctx.author)
        
        targetStory = None
        for story in stories:
            if story.title == targetTitle:
                targetStory = story
                break
        if not targetStory:
            await dmError(ctx, f"Could not find a story you've created with the given name ({targetTitle}).")
            return
        
        changeCallback(targetStory)
        
        await StoryCog.updateMessageWithStories(ctx.author, foundMessage, stories)
    
    @staticmethod
    def getStoriesFromMessage(message: Message, targetAuthor: User) -> list[Story]:
        """ Creates a list of stories from a message.
            Makes the author of all created stories the targetAuthor, confirmed with StoryCog.isMessageForAuthor. """
        
        storiesRaw = message.content.split(separator)
        writerRaw, *storiesRaw = storiesRaw
        
        stories: list[Story] = []
        for storyRaw in storiesRaw:
            story = Story.newFromText(targetAuthor, storyRaw)
            print(story)
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
    async def settitle(self, ctx: Context, targetTitle: str, newTitle: str):
        """ Finds the story with the given title and alters its title. """
            
        def changeTitle(story: Story):
            story.title = newTitle
        await self.setStoryAttr(ctx, targetTitle, changeTitle)

    @command(ignore_extra=False)
    async def setgenres(self, ctx: Context, targetTitle: str, *newGenres: str):
        """ Finds the story with the given title and alters its genres. """
        
        newGenres = [genre.capitalize() for genre in newGenres]
        
        for genre in newGenres:
            if not genre in allGenres:
                await dmError(ctx, f"The genre specified ({genre}) is not one of:\n  " + "  \n".join(allGenres))
                return
        
        def changeGenres(story: Story):
            story.genres = newGenres
        await self.setStoryAttr(ctx, targetTitle, changeGenres)
    
    @command(ignore_extra=False)
    async def setrating(self, ctx: Context, targetTitle: str, newRating: str):
        """ Finds the story with the given title and alters its rating. """
        
        if not newRating in allRatings:
            await dmError(ctx, f"The rating for your story must be one of {allRatings}, not {newRating}.")
            return
        
        def changeRating(story: Story):
            story.rating = newRating
        await self.setStoryAttr(ctx, targetTitle, changeRating)
    
    @command(ignore_extra=False)
    async def setratingreason(self, ctx: Context, targetTitle: str, newReason: str):
        """ Finds the story with the given title and alters the reason for its rating. """
        
        def changeReason(story: Story):
            story.ratingReason = newReason
        await self.setStoryAttr(ctx, targetTitle, changeReason)

    @command(ignore_extra=False)
    async def addcharacter(self, ctx: Context, targetTitle: str, charName: str, charSpecies: str):
        """ Finds the story with the given title and adds to it a new character with the given name and species. """
        
        newChar = Character(charName, charSpecies)
        
        def changeCharacter(story: Story):
            story.characters.append(newChar)
        await self.setStoryAttr(ctx, targetTitle, changeCharacter)
    
    @command(ignore_extra=False)
    async def removecharacter(self, ctx: Context, targetTitle: str, charName: str):
        """ Finds the story with the given title and removes from it a character with the given name. 
            Note: does not send an error message if there is no character with the given name. """
        
        def changeCharacter(story: Story):
            found = None
            for char in story.characters:
                if char.name == charName:
                    found = char
            if found:
                story.characters.remove(found)
        await self.setStoryAttr(ctx, targetTitle, changeCharacter)
