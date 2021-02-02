
import sources.text as T
from sources.general import REF_COMMAND, REF_COMMAND_PLAIN

cogName = "Retrieval Cog"
cogDescription = "This part of the bot aids in finding stories and other story-related utilities."

class cmd:
    setArchiveChannel = {
        "name": "setarchivechannel",
        "help": "Sets the archive channel for this server."
    }
    archiveGuide = {
        "name": "archiveguide",
        "aliases": ["archivehelp"],
        "help": f"Shows a help message that explains how to add a story through the {T.ARCH.cogName}."
    }
    listGenres = {
        "name": "listgenres",
        "help": f"Gets a list of possible story genres to be added with {REF_COMMAND(T.ARCH.cmd.addGenre)}."
    }
    listSites = {
        "name": "listsites",
        "help": f"Gets a list of valid site abbreviations to be used with {REF_COMMAND(T.ARCH.cmd.addLink)}."
    }
    listRatings = {
        "name": "listratings",
        "help": f"Gets a list of valid ratings to be set with {REF_COMMAND(T.ARCH.cmd.setRating)}."
    }
    randomStory = {
        "name": "randomstory",
        "help": f"Gets a random story from the story archive."
    }
    searchByAuthor = {
        "name": "searchbyauthor",
        "help": f"Gets a link to the archive post for a given user."
    }


_listText = lambda item, joinedItems, suffix=True: f"Below is each valid {item}: ```\n{joinedItems}```" + ("" if not suffix else f"\nIf your {item} is not listed here, please let a moderator know.")
listGenre = _listText("genre", "\n".join(T.ARCH.ALL_GENRES))
listSiteAbbrs = _listText("site abbreviation", "\n".join([f"{name} (used for {T.ARCH.ALL_SITE_ABBREVIATIONS[name]})" for name in T.ARCH.ALL_SITE_ABBREVIATIONS]))
listRatings = _listText("rating", ", ".join(T.ARCH.ALL_RATINGS), False)

errorRandomStoryFail = "Couldn't find a story."

embedStoryTitle = lambda title: title
embedStoryDescription = lambda author, summary, jumpURL: f"by {author}\n" + (f"```{summary}```" if summary else "No description") + "\n" + jumpURL

embedSearchAuthorTitle = lambda name: f"Stories by {name}"
embedSearchAuthorDescription = lambda jump, name: f"Archive post:\n{jump}" if jump else f"{name} doesn't have any posts in the story archive."

embedGuideTitle = "Archive guide"
embedGuideDescription = f""" This embed will tell you how to set up a story in your server's archive channel.

To start, use the {REF_COMMAND(T.ARCH.cmd.addCharacter)} command to add a new story, and give it your story's name.
```{REF_COMMAND_PLAIN(T.ARCH.cmd.addCharacter)} Null Protocol```

Next, you may use the {REF_COMMAND(T.ARCH.cmd.addGenre)} command to give your story a genre - these can be found using the command {REF_COMMAND(cmd.listGenres)}. If you want to add multiple genres at a time, separate each with a space.
```{REF_COMMAND_PLAIN(T.ARCH.cmd.addGenre)} Adventure Friendship```

To add a rating to your story, use the {REF_COMMAND(T.ARCH.cmd.setRating)} command. Possible ratings can be found using the command {REF_COMMAND(cmd.listRatings)}.
```{REF_COMMAND_PLAIN(T.ARCH.cmd.setRating)} T```

If you want, you may add a reason for your rating via the {REF_COMMAND(T.ARCH.cmd.setRatingReason)} command.
```{REF_COMMAND_PLAIN(T.ARCH.cmd.setRatingReason)} Swearing, ||violence||```

Characters can be added to your story using the {REF_COMMAND(T.ARCH.cmd.addCharacter)} command. Characters have a species and an optional name. If your character doesn't have/need a name, you can simply enter their species. If your character needs both a species and a name, give their name followed by a vertical pipe ("|") followed by their species (see examples).
```{REF_COMMAND_PLAIN(T.ARCH.cmd.addCharacter)} Quil | Cyndaquil
{REF_COMMAND_PLAIN(T.ARCH.cmd.addCharacter)} Orial | Mienfoo
{REF_COMMAND_PLAIN(T.ARCH.cmd.addCharacter)} Guildmaster Kess | Archeops
{REF_COMMAND_PLAIN(T.ARCH.cmd.addCharacter)} Yveltal```

Next you can add a summary to your story with the {REF_COMMAND(T.ARCH.cmd.setSummary)} command. If you want to use newlines in your summary, you will have to surround it in quotes.
```{REF_COMMAND_PLAIN(T.ARCH.cmd.setSummary)} Forterra has been swept by the new pandemic mystery dungeons... (etc.)```

Last in the story are the links, which can be added using the {REF_COMMAND(T.ARCH.cmd.addLink)} command. This command takes the abbreviation for the site and the URL itself. The list of valid site abbreviations can be found using the {REF_COMMAND(cmd.listSites)} command.
```{REF_COMMAND_PLAIN(T.ARCH.cmd.addLink)} AO3 https://archiveofourown.org/```

Note - if you wish to perform multiple commands at once, prepend your message with {REF_COMMAND(T.ARCH.cmd.multi)}.
```
{REF_COMMAND_PLAIN(T.ARCH.cmd.multi)}
{T.ARCH.cmd.addStory["name"]} Null Protocol
{T.ARCH.cmd.addGenre["name"]} Adventure Frienship
{T.ARCH.cmd.setRating["name"]} T
...
```
"""
