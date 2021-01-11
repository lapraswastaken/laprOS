

from discord.message import Message
from discord.user import User
import re

ratingPat = re.compile(r"(.+?)\s*\((.+)\)")
charsPat = re.compile(r"(\S+?)\s*\|\s*(\S+?)(?:,|$)")
linkPat = re.compile(r"- <(.+)>")

class Character:
    def __init__(self, name: str, species: str):
        self.name = name
        self.species = species
    
    def __str__(self):
        return self.name + " | " + self.species

class Story:
    def __init__(self, title: str, authorUser: User, genres: list[str]=[], rating: str="", ratingReason: str="", characters: list[Character]=[], summary: str="", links: list[str]=[]):
        self.title = title
        self.authorUser = authorUser
        
        self.genres: list[str] = genres
        self.rating = rating
        self.ratingReason = ratingReason
        self.characters: list[Character] = characters
        self.summary = summary
        self.links: list[str] = links
    
    def __str__(self):
        return f"Title: {self.title}\nAuthor ID: {self.authorUser.id}\nGenres: {self.genres}\nRating: {self.rating}\nReason: {self.ratingReason}\nCharacters: {self.characters}\nSummary: {self.summary}\nLinks: {self.links}"
    
    def toText(self):
        genresStr = ", ".join(self.genres)
        ratingStr = self.rating + (f" ({self.ratingReason})" if self.ratingReason else "")
        charsStr = ", ".join([str(char) for char in self.characters])
        linksStr = "\n".join(["- <" + link + ">" for link in self.links])
        summaryStr = f"```\n{self.summary}\n```" if self.summary else ""
        return "" + \
            f"**Title**: {self.title}\n" + \
            f"**Genres**: {genresStr}\n" + \
            f"**Rating**: {ratingStr}\n" + \
            f"**Main Characters**: {charsStr}\n" + \
            f"**Summary**:\n{summaryStr}\n" + \
            f"**Links**:\n{linksStr}"
    
    @staticmethod
    def newFromText(writerUser: User, text: str):
        lines = text.split("\n")
        print(lines)
        getter = lambda i: lines[i].split(":", 1)[1].strip()
        title = getter(0)
        genres = getter(1).split(", ")
        ratingRaw = getter(2)
        ratingMatch = ratingPat.search(ratingRaw)
        rating, reason = ratingMatch.groups() if ratingMatch else ["", ""]
        charsRaw = getter(3)
        chars: list[Character] = []
        for charName, charSpecies in charsPat.findall(charsRaw):
            char = Character(charName, charSpecies)
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
        links = []
        while i < len(lines):
            if not lines[i].startswith("Links:"):
                linksMatch = linkPat.search(lines[i])
                if linksMatch:
                    links.append(linksMatch.group(1))
            i += 1
        
        return Story(title, writerUser, genres, rating, reason, chars, summary, links)
