
from __future__ import annotations
import re
from typing import Optional

import sources.ids as IDS

MAX_TITLE_LEN = 75
MAX_RATING_REASON_LEN = 100
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
    "GD": "Google Docs",
    "CF": "Comic Fury",
    "TB": "Tumblr",
    "CL": "Canalave Library",
    "SF": "Serebii Forums",
}

BOT_PREFIX = "lap."

NEWLINE = "\n"

stripLines = lambda text: "\n".join([line.strip() for line in text.split("\n")])
oxfordComma = lambda list: ', '.join(list[:-1] + [f"and {list[-1]}"]) if len(list) != 2 else f"{list[0]} and {list[1]}"

class Cmd:
    def __init__(self, *args, usage: list[str]=None, parent: Optional[Cmd]=None, **kwargs):
        self.name: str = args[0]
        self.aliases: list[str] = args[1:-1]
        self.desc: list[str] = args[-1]
        self.parent = parent
        self.qualifiedName = self.name
        if self.parent:
            self.qualifiedName = f"{parent.qualifiedName} {self.qualifiedName}"
        
        if usage:
            self.desc += "\n**Usage:**```\n" + "\n".join([f"{BOT_PREFIX}{self.qualifiedName} {case}" for case in usage]) + "```"
        
        for key, val in kwargs.items():
            setattr(self, key, val)
        
        self.desc = stripLines(self.desc)
        
        self.meta = {"name": self.name, "aliases": self.aliases, "help": self.desc}
        self.ref = f"{BOT_PREFIX}{self.name}"
        self.refF = f"`{self.ref}`"

LAPROS_GRAPHIC_URL = "https://cdn.discordapp.com/attachments/284520081700945921/799416249738067978/laprOS_logo.png"

MENTION_ME = f"<@{IDS.MY_USER_ID}>"
EMPTY = "\u200b"

LINK_RE = re.compile(r"(?!<)(https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/\/=]*))(?!>)")

escapeLinks = lambda text: LINK_RE.sub(r"<\1>", text)
