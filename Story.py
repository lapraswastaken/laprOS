
from __future__ import annotations
from Archive import Character, Genre, Link, Story
import discord
import pickle
import re
from typing import Optional

ratingPat = re.compile(r"(.+?)(?: \((.+)\))?")
charsPat = re.compile(r" ?(.+?)(?: \| (.+?))?(?:,|$)")
linkPat = re.compile(r"- (\w+): <(.+)>")
    
def newFromText(text: str):
    lines = text.split("\n")
    getter = lambda i: lines[i].split(":", 1)[1].strip()
    title = getter(0)
    genres = [(genre,) for genre in getter(1).split(", ") if genre]
    ratingRaw = getter(2).split("(", 1)
    rating = ratingRaw[0].strip()
    reason = ""
    if len(ratingRaw) == 2:
        reason = ratingRaw[1][:-1].strip()
    charsRaw = getter(3)
    chars: list[Character] = []
    for left, right in charsPat.findall(charsRaw):
        char = (right if right else left, left if right else None)
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
        linksMatch = linkPat.search(lines[i])
        if linksMatch:
            links.append((linksMatch.group(1), linksMatch.group(2)))
        i += 1
    
    return Story(title, genres, rating, reason, chars, summary, links)

digitsPat = re.compile(r"(\d+)")
SEPARATOR = "\n\n=====\n\n"

async def getStoriesFromMessage(message: discord.Message) -> list[Story]:
    """ Creates a list of stories from a message.
        Makes the author of all created stories the targetAuthor, confirmed with StoryCog.isMessageForAuthor. """
    
    writerRaw = message.content.split(SEPARATOR)[0]
    match = digitsPat.search(writerRaw)
    if not match: return None, None
    authorID =  int(match.group(1))
    targetAuthor = await message.guild.fetch_member(authorID)
    print(f"[AUTHOR: {targetAuthor}]")
    
    storiesRaw = message.content.split(SEPARATOR)[1:]
    
    stories: list[Story] = []
    for storyRaw in storiesRaw:
        story = newFromText(storyRaw)
        stories.append(story)
    return targetAuthor, stories
