

from typing import Optional
import discord
import re

ratingPat = re.compile(r"(.+?)(?:\s*\((.+)\))?")
charsPat = re.compile(r"\s*(.+?)(?:\s*\|\s*(.+?))?(?:,|$)")
linkPat = re.compile(r"- (.+): <(.+)>")

class Character:
    def __init__(self, species: str, name: Optional[str]):
        self.species = species
        self.name = name
    
    def __str__(self):
        return (self.species if not self.name else self.name) + ((" | " + self.species) if self.name else "")

class Story:
    def __init__(self, title: str, author: discord.Member, genres: list[str]=[], rating: str="", ratingReason: str="", characters: list[Character]=[], summary: str="", links: dict[str, str]={}):
        self.title = title
        self.author = author
        
        self.genres = genres
        self.rating = rating
        self.ratingReason = ratingReason
        self.characters = characters
        self.summary = summary
        self.links = links
    
    def __str__(self):
        return f"Title: {self.title}\nAuthor ID: {self.author.id}\nGenres: {self.genres}\nRating: {self.rating}\nReason: {self.ratingReason}\nCharacters: {self.characters}\nSummary: {self.summary}\nLinks: {self.links}"
    
    def toText(self):
        genresStr = ", ".join(self.genres)
        ratingStr = self.rating + (f" ({self.ratingReason})" if self.ratingReason else "")
        charsStr = ", ".join([str(char) for char in self.characters])
        linksStr = "\n".join([f"- {linkName}: <{self.links[linkName]}>" for linkName in sorted(self.links.keys())])
        summaryStr = f"```\n{self.summary}\n```" if self.summary else ""
        return "" + \
            f"**Title**: {self.title}\n" + \
            f"**Genres**: {genresStr}\n" + \
            f"**Rating**: {ratingStr}\n" + \
            f"**Main Characters**: {charsStr}\n" + \
            f"**Summary**:\n{summaryStr}\n" + \
            f"**Links**:\n{linksStr}"
    
    @staticmethod
    def newFromText(author: discord.Member, text: str):
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
        
        return Story(title, author, genres, rating, reason, chars, summary, links)
