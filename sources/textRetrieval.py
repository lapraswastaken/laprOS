
import sources.textArchive as T_ARCH
import sources.general as T_GEN

cogName = "Retrieval Cog"
cogDescription = "This part of the bot aids in finding stories and other story-related utilities."

cmdSetArchiveChannel = "setarchivechannel"
cmdArchiveGuide = "archiveguide"
cmdListGenres = "listgenres"

cmdSetArchiveChannelHelp = "Sets the archive channel for this server."
cmdArchiveGuideHelp = "Shows a help message that explains how to add a story to the archive."
cmdListGenresHelp = "Get a list of possible story genres to be added with "


_listText = lambda item, joinedItems, suffix=True: f"Below is each valid {item}: ```\n{joinedItems}```" + ("" if not suffix else f"\nIf your {item} is not listed here, please let {T_GEN.mentionMe} or a moderator know.")
listGenre = _listText("genre", "\n".join(T_ARCH.ALL_GENRES))
listSiteAbbrs = _listText("site abbreviation", "\n".join([f"{name} (used for {T_ARCH.ALL_SITE_ABBREVIATIONS[name]})" for name in T_ARCH.ALL_SITE_ABBREVIATIONS]))
listRatings = _listText("rating", ", ".join(T_ARCH.ALL_RATINGS), False)

errorRandomStoryFail = "Couldn't find a story."

embedStoryTitle = lambda title: title
embedStoryDescription = lambda author, summary, jumpURL: f"by {author}\n" + (f"```{summary}```" if summary else "No description") + "\n" + jumpURL

embedSearchAuthorTitle = lambda name: f"Stories by {name}"
embedSearchAuthorDescription = lambda jump, name: f"Archive post:\n{jump}" if jump else f"{name} doesn't have any posts in the story archive."

embedGuideTitle = "Archive guide"
embedGuideDescription = """ This embed will tell you how to set up a story in your server's archive channel.

To start, use the `lap.addstory` command to add a new story, and give it your story's name in quotes.
```lap.addstory "Null Protocol"```

Next, you may use the `lap.addgenre` command to give your story a genre - these can be found using the command `lap.listgenres`. You can use this multiple times to add multiple genres to your story.
```lap.addgenre Adventure
lap.addgenre Friendship```

To add a rating to your story, use the `lap.setrating` command. Possible ratings can be found using the command `lap.listratings`.
```lap.setrating T```

If you want, you may add a reason why you rated your story the way you did with the `lap.setratingreason` command. This can be anything and can include spoilers if you wish. Note that the reason must be surrounded in quotes.
```lap.setratingreason "Swearing, ||violence||"```

Characters can be added to your story using the `lap.addcharacter` command. Give it a species followed by a name (if applicable / wanted). If a species or name has spaces in it, you will need to surround it in quotes.
```lap.addcharacter Cyndaquil Quil
lap.addcharacter Mienfoo Orial
lap.addcharacter Archeops
lap.addcharacter Yveltal "The Living God"```

Next you can add a summary to your story with the `lap.setsummary` command. Note that the summary must be surrounded in quotes.
```lap.setsummary "Forterra has been swept by the new pandemic mystery dungeons... etc."```

Last in the list are the links, which can be added using the `lap.addlink` command. This command takes the abbreviation for the site and the URL itself. The list of valid site abbreviations can be found using the `lap.listsites` command.
```lap.addlink AO3 https://archiveofourown.org/```

Note - if you wish to perform multiple commands at once, prepend your message with lap.multi.
```
lap.multi
addstory "Null Protocol"
addgenre Adventure
addgenre Frienship
setrating T
...
```
"""
