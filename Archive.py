
from __future__ import annotations

import pickle
from typing import Callable, Optional

ALL_RATINGS = ["K", "K+", "T", "M"]
ALL_GENRES = [
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
ALL_LINK_NAMES = {
    "AO3": "Archive Of Our Own",
    "FFN": "FanFiction.Net",
    "TR": "Thousand Roads",
    "RR": "Royal Road",
    "DA": "Deviant Art",
    "WP": "WattPad",
    "GD": "Google Docs"
}

def isValidGenre(name: str): return name in ALL_GENRES
def isValidSiteAbbr(name: str): return name in ALL_LINK_NAMES
def isValidRating(name: str): return name in ALL_RATINGS

class InvalidNameException(Exception): pass
class DuplicateException(Exception): pass
class NotFoundException(Exception): pass

class Prioritied:
    def __init__(self, priority: Optional[int]=None):
        self.priority = priority if priority != None else 0
    
    def increment(self):
        return self.priority + 1
    
    @staticmethod
    def key(obj: Prioritied):
        return obj.priority

class Genre(Prioritied):
    def __init__(self, name: str, priority: Optional[int]=None):
        super().__init__(priority)
        
        self.name = name

class Character(Prioritied):
    def __init__(self, species: str, name: str, priority: Optional[int]=None):
        super().__init__(priority)
        
        self.species = species
        self.name = name
    
    def __eq__(self, other: object):
        if not isinstance(other, Character): return False
        return self.species == other.species and self.name == other.name
    
    def format(self):
        if self.species and self.name:
            return f"{self.name} | {self.species}"
        elif self.species:
            return self.species
        else:
            return self.name

class Link(Prioritied):
    def __init__(self, siteAbbr: str, url: str, priority: Optional[int]=None):
        super().__init__(priority)
        
        self.siteAbbr = siteAbbr
        self.url = url

class Story(Prioritied):
    def __init__(self, title: str, genres: list[Genre]=[], rating: str="", ratingReason: str="", characters: list[Character]=[], summary: str="", links: list[Link]=[], priority: Optional[int]=None):
        super().__init__(priority)
        
        self.title = title
        self.genres = genres
        self.rating = rating
        self.ratingReason = ratingReason
        self.characters = characters
        self.summary = summary
        self.links = links
    
    def format(self):
        genresStr = ", ".join(sorted(self.genres, key=Prioritied.key))
        ratingStr = self.rating
        if self.ratingReason:
            ratingStr += f" ({self.ratingReason})"
        charsStr = ", ".join([char.format() for char in sorted(self.characters, Prioritied.key)])
        summaryStr = f"```\n{self.summary}\n```" if self.summary else ""
        linksStr = "\n".join([f"- {link.siteAbbr}: <{link.url}>" for link in sorted(self.links, Prioritied.key)])
        
        return "" + \
            f"**Title**: {self.title}\n" + \
            f"**Genres**: {genresStr}\n" + \
            f"**Rating**: {ratingStr}\n" + \
            f"**Main Characters**: {charsStr}\n" + \
            f"**Summary**:\n{summaryStr}\n" + \
            f"**Links**:\n{linksStr}"
    
    def setTitle(self, newTitle: str):
        self.title = newTitle
    
    def addGenre(self, newName: str, newPriority: Optional[int]=None):
        if not isValidGenre(newName):
            raise InvalidNameException()
        if newName in [genre.name for genre in self.genres]:
            raise DuplicateException()
        if newPriority == None and self.genres:
            newPriority = self.genres[-1].increment()
        self.genres.append(Genre(newName, newPriority))
    
    def removeGenre(self, targetName: str):
        fetched: Optional[Genre] = None
        for genre in self.genres:
            if genre.name == targetName:
                fetched = genre
        if not fetched:
            raise NotFoundException()
        self.genres.remove(fetched)
    
    def setRating(self, newRating: str):
        if not isValidRating(newRating):
            raise InvalidNameException()
        self.rating = newRating
    
    def setRatingReason(self, newReason: str):
        self.ratingReason = newReason
    
    def addCharacter(self, newSpecies: str, newName: Optional[str]=None, newPriority: Optional[int]=None):
        if newPriority == None and self.characters:
            newPriority = self.characters[-1].increment()
        newChar = Character(newSpecies, newName, newPriority)
        if any([newChar == char for char in self.characters]):
            raise DuplicateException()
        self.characters.append(newChar)
    
    def removeCharacter(self, targetSpecies: str, targetName: Optional[str]=None):
        targetChar = Character(targetSpecies, targetName)
        fetched: Optional[Character] = None
        for char in self.characters:
            if targetChar.name:
                if char == targetChar:
                    fetched = char
            else:
                if char.species == targetChar.species:
                    fetched = char
        if not fetched:
            raise NotFoundException()
        self.characters.remove(fetched)
    
    def setSummary(self, newSummary: str):
        self.summary = newSummary
    
    def addLink(self, newSiteAbbr: str, newURL: str, newPriority: Optional[int]=None):
        if not isValidSiteAbbr(newSiteAbbr):
            raise InvalidNameException()
        if newPriority == None and self.links:
            newPriority = self.links[-1].increment()
        newLink = Link(newSiteAbbr, newURL, newPriority)
        if newLink.siteAbbr in [link.siteAbbr for link in self.links]:
            raise DuplicateException()
        self.links.append(newLink)

    def removeLink(self, targetSiteAbbr: str):
        fetched: Optional[Link] = None
        for link in self.links:
            if link.siteAbbr == targetSiteAbbr:
                fetched = link
        if not fetched:
            raise NotFoundException()
        self.links.remove(fetched)

class Post:
    def __init__(self, authorID: int, messageIDs: list[int], stories: list[Story]=[]):
        self.authorID = authorID
        self.messageIDs = messageIDs
        self.stories = stories
    
    def addStory(self, newStory: Story):
        if newStory.title in [story.title for story in self.stories]:
            raise DuplicateException()
        self.stories.append(newStory)

class Archive:
    def __init__(self, channelID: int, posts: dict[int, Post]={}):
        self.channelID = channelID
        self.posts = posts
    
    def createPost(self, authorID: int, messageID: int):
        if authorID in self.posts:
            raise DuplicateException()
        self.posts[authorID] = Post(authorID, messageID)
    
    def getPost(self, authorID: int):
        if not authorID in self.posts:
            raise NotFoundException()
        return self.posts[authorID]

class OverArch:
    def __init__(self, archives: dict[int, Archive]={}):
        self.archives = archives
    
    @staticmethod
    def read():
        with open("./sources/overarch.p", "r") as f:
            return pickle.load(f)
    
    def write(self):
        with open("./sources/overarch.p", "w") as f:
            pickle.dump(self, f)
        
    def addArchive(self, guildID: int, channelID: int):
        if guildID in self.archives:
            raise DuplicateException()
        self.archives[guildID] = Archive(channelID)
    
    def getArchive(self, guildID):
        if not guildID in self.archives:
            raise NotFoundException()
        return self.archives[guildID]

OVERARCH = OverArch.read()
if not OVERARCH:
    OVERARCH = OverArch()
