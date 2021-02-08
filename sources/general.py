
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
    "GD": "Google Docs"
}

BOT_PREFIX = "lap."

NEWLINE = "\n"

stripLines = lambda text: "\n".join([line.strip() for line in text.split("\n")])

class Cmd:
    def __init__(self, *args, usage: list[str]=None, **kwargs):
        self.name: str = args[0]
        self.aliases: list[str] = args[1:-1]
        self.desc: list[str] = args[-1]
        
        if usage:
            self.desc += "\n**Usage:**```\n" + "\n".join([f"{BOT_PREFIX}{self.name} {case}" for case in usage]) + "```"
        
        for key, val in kwargs.items():
            setattr(self, key, val)
        
        self.desc = stripLines(self.desc)
        
        self.meta = {"name": self.name, "aliases": self.aliases, "help": self.desc}
        
    def ref(self):
        """ Returns a string with the bot's prefix and the name of this command. """
        return f"{BOT_PREFIX}{self.name}"
    def refF(self):
        """ Returns a string with the bot's prefix and the name of this command, formatted as a code snippet in Markdown. """
        return f"`{BOT_PREFIX}{self.name}`"

LAPROS_GRAPHIC_URL = "https://cdn.discordapp.com/attachments/284520081700945921/799416249738067978/laprOS_logo.png"

MENTION_ME = f"<@{IDS.MY_USER_ID}>"
EMPTY = "\u200b"

REF_COMMAND = lambda command: f'`{BOT_PREFIX}{command["name"]}`'
REF_COMMAND_PLAIN = lambda command: f'{BOT_PREFIX}{command["name"]}'
