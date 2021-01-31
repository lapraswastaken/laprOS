
from __future__ import annotations

import json
import pickle
import random
import re
from typing import Callable, Optional, Union

MAX_TITLE_LEN = 50
MAX_RATING_REASON_LEN = 50
MAX_CHAR_SPECIES_LEN = 20
MAX_CHAR_NAME_LEN = 20
MAX_SUMMARY_LEN = 1000
MAX_LINK_URL_LEN = 100

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
ALL_SITE_ABBREVIATIONS = {
    "AO3": "Archive Of Our Own",
    "FFN": "FanFiction.Net",
    "TR": "Thousand Roads",
    "RR": "Royal Road",
    "DA": "Deviant Art",
    "WP": "WattPad",
    "GD": "Google Docs"
}

def isValidGenre(name: str): return name in ALL_GENRES
def isValidSiteAbbr(name: str): return name in ALL_SITE_ABBREVIATIONS
def isValidRating(name: str): return name in ALL_RATINGS

class InvalidNameException(Exception): pass
class DuplicateException(Exception): pass
class NotFoundException(Exception): pass
class MaxLenException(Exception): pass
class MaxSpeciesLenException(MaxLenException): pass
class MaxNameLenException(MaxLenException): pass

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
    
    def toJSON(self):
        return (self.name, self.priority)

class Character(Prioritied):
    def __init__(self, species: str, name: str="", priority: Optional[int]=None):
        super().__init__(priority)
        
        self.species = species
        self.name = name
    
    def toJSON(self):
        return (self.species, self.name, self.priority)
    
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
    
    def toJSON(self):
        return (self.siteAbbr, self.url, self.priority)

class Story(Prioritied):
    def __init__(self, title: str, genres: Optional[list[tuple]]=None, rating: Optional[str]=None, ratingReason: Optional[str]=None, characters: Optional[list[Character]]=None, summary: Optional[str]=None, links: Optional[list[Link]]=None, priority: Optional[int]=None):
        super().__init__(priority)
        if len(title) > MAX_TITLE_LEN:
            raise MaxLenException()
        
        self.title = title
        self.genres: list[Genre] = [] if not genres else [Genre(*genre) for genre in genres]
        self.rating = "" if not rating else rating
        self.ratingReason = "" if not ratingReason else ratingReason
        self.characters: list[Character] = [] if not characters else [Character(*character) for character in characters]
        self.summary = "" if not summary else summary
        self.links: list[Link] = [] if not links else [Link(*link) for link in links]
    
    def toJSON(self):
        json = {
            "title": self.title,
            "genres": [genre.toJSON() for genre in self.genres],
            "rating": self.rating,
            "ratingReason": self.ratingReason,
            "characters": [character.toJSON() for character in self.characters],
            "summary": self.summary,
            "links": [link.toJSON() for link in self.links],
            "priority": self.priority
        }
        return json
    
    @staticmethod
    def fromJSON(json: dict[str, Union[str, list[str]]]):
        return Story(
            json["title"],
            [Genre(*tup) for tup in json["genres"]],
            json["rating"],
            json["ratingReason"],
            [Character(*tup) for tup in json["characters"]],
            json["summary"],
            [Link(*tup) for tup in json["links"]],
            json["priority"]
        )
    
    def format(self):
        genresStr = ", ".join([genre.name for genre in sorted(self.genres, key=Prioritied.key)])
        ratingStr = self.rating
        if self.ratingReason:
            ratingStr += f" ({self.ratingReason})"
        charsStr = ", ".join([char.format() for char in sorted(self.characters, key=Prioritied.key)])
        summaryStr = f"```\n{self.summary}\n```" if self.summary else ""
        linksStr = "\n".join([f"- {link.siteAbbr}: <{link.url}>" for link in sorted(self.links, key=Prioritied.key)])
        
        string = "" + \
            f"**Title**: {self.title}\n" + \
            f"**Genres**: {genresStr}\n" + \
            f"**Rating**: {ratingStr}\n" + \
            f"**Main Characters**: {charsStr}\n" + \
            f"**Summary**:\n{summaryStr}\n" + \
            f"**Links**:\n{linksStr}"
        return string
    
    def cite(self):
        return f"\"{self.title}\""
    
    def setTitle(self, newTitle: str):
        if len(newTitle) > MAX_TITLE_LEN:
            raise MaxLenException()
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
        if len(newReason) > MAX_RATING_REASON_LEN:
            raise MaxLenException()
        self.ratingReason = newReason
    
    def addCharacter(self, newSpecies: str, newName: str="", newPriority: Optional[int]=None):
        if len(newSpecies) > MAX_CHAR_SPECIES_LEN:
            raise MaxSpeciesLenException()
        if len(newName) > MAX_CHAR_NAME_LEN:
            raise MaxNameLenException()
        if newPriority == None and self.characters:
            newPriority = self.characters[-1].increment()
        newChar = Character(newSpecies, newName, newPriority)
        if any([newChar == char for char in self.characters]):
            raise DuplicateException()
        self.characters.append(newChar)
    
    def removeCharacter(self, targetSpecies: str, targetName: str=""):
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
        if len(newSummary) > MAX_SUMMARY_LEN:
            raise MaxLenException()
        self.summary = newSummary
    
    def addLink(self, newSiteAbbr: str, newURL: str, newPriority: Optional[int]=None):
        if len(newURL) > MAX_LINK_URL_LEN:
            raise MaxLenException()
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

charsPat = re.compile(r" ?(.+?)(?: \| (.+?))?(?:,|$)")
linkPat = re.compile(r"- ([A-Z]+): <(.+)>")

def convertOldFromText(text: str):
    lines = text.split("\n")
    getter = lambda i: lines[i].split(":", 1)[1].strip()
    title = getter(0)
    genres = [genre for genre in getter(1).split(", ") if genre]
    ratingRaw = getter(2).split("(", 1)
    rating = ratingRaw[0].strip()
    reason = ""
    if len(ratingRaw) == 2:
        reason = ratingRaw[1][:-1].strip()
    charsRaw = getter(3)
    chars: list[Character] = []
    for left, right in charsPat.findall(charsRaw):
        char = Character(right if right else left, left if right else None)
        chars.append(char)
    summary = []
    endSum = False
    i = 6 # the index of the first line of the summary
    while not endSum:
        if lines[i].startswith("```"):
            endSum = True
        elif lines[i].startswith("**Links**:"):
            endSum = True
        else:
            summary.append(lines[i])
        i += 1
    summary = "\n".join(summary)
    links = {}
    i += 1
    while i < len(lines):
        linksMatch = linkPat.search(lines[i])
        if linksMatch:
            links[linksMatch.group(1)] = linksMatch.group(2)
        i += 1
    
    return Story(title, genres, rating, reason, chars, summary, links)

class Post:
    def __init__(self, authorID: int, messageID: Optional[int]=None, stories: Optional[list[dict]]=None, focused: Optional[int]=None):
        self.authorID = authorID
        self.messageID= messageID
        self.stories: list[Story] = [] if not stories else [Story(**story) for story in stories]
        self.focused = focused
    
    def toJSON(self):
        json = {
            "authorID": self.authorID,
            "messageID": self.messageID,
            "focused": self.focused,
            "stories": [story.toJSON() for story in self.stories]
        }
        return json
    
    def format(self):
        string = ""
        for i, story in enumerate(self.stories):
            if i == self.focused:
                string += f"**\> {story.title}**\n"
            else:
                string += f"{story.title}\n"
        
        return string
    
    def addStory(self, newStory: Story):
        if newStory.title in [story.title for story in self.stories]:
            raise DuplicateException()
        self.stories.append(newStory)
    
    def getStory(self, targetTitle: Optional[str]=None):
        if not targetTitle:
            return self.stories[self.focused]
        for story in self.stories:
            if story.title == targetTitle:
                return story
        raise NotFoundException()

    def removeStory(self, targetTitle: str):
        retrieved: Optional[Story] = None
        for story in self.stories:
            if story.title == targetTitle:
                retrieved = story
        if not retrieved:
            raise NotFoundException()
        self.stories.remove(retrieved)
    
    def getFocusedStory(self) -> Story:
        return self.stories[self.focused]
    
    def focusStory(self, story: Story):
        index = self.stories.index(story)
        self.focused = index
    
    def getRandomStory(self):
        return random.choice(self.stories)

class Archive:
    def __init__(self, channelID: int, posts: Optional[dict[str, dict]]=None):
        self.channelID = channelID
        self.posts: dict[int, Post] = {}
        if posts:
            for authorID in posts:
                self.posts[int(authorID)] = Post(**posts[authorID])
    
    def toJSON(self):
        json = {
            "channelID": self.channelID,
            "posts": {}
        }
        for authorID in self.posts:
            json["posts"][authorID] = self.posts[authorID].toJSON()
        return json
    
    def createPost(self, authorID: int):
        if authorID in self.posts:
            raise DuplicateException()
        self.posts[authorID] = Post(authorID)
        return self.posts[authorID]
    
    def getPost(self, authorID: int):
        return self.posts.get(authorID)
    
    def getPostByMessageID(self, targetMessageID):
        for authorID in self.posts:
            post = self.posts[authorID]
            if post.messageID == targetMessageID:
                return post
        raise NotFoundException()
    
    def getRandomPost(self):
        return random.choice(list(self.posts.values()))
    
    def getAllStories(self):
        allStories = []
        for post in self.posts.values():
            allStories += post.stories
        return allStories

class OverArch:
    def __init__(self, archives: dict[str, dict]=None):
        self.archives: dict[int, Archive] = {}
        if archives:
            for guildID in archives:
                self.archives[int(guildID)] = Archive(**archives[guildID])
    
    @staticmethod
    def read():
        with open("./sources/archives.json", "r") as f:
            return OverArch(**json.loads(f.read()))
    
    def write(self):
        with open("./sources/archives.json", "w") as f:
            f.write(json.dumps(self.toJSON()))
    
    def toJSON(self):
        json = {
            "archives": {}
        }
        for guildID in self.archives:
            json["archives"][guildID] = self.archives[guildID].toJSON()
        return json
        
    def addArchive(self, guildID: int, channelID: int):
        if guildID in self.archives:
            raise DuplicateException()
        self.archives[guildID] = Archive(channelID)
        return self.archives[guildID]
    
    def getArchive(self, guildID):
        return self.archives.get(guildID)
    
    def isValidChannelID(self, channelID: int):
        return channelID in [archive.channelID for archive in self.archives.values()]

OVERARCH = OverArch.read()
if not OVERARCH:
    OVERARCH = OverArch()
    OVERARCH.write()
