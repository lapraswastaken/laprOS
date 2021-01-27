
from Archive import ALL_GENRES, ALL_RATINGS, ALL_SITE_ABBREVIATIONS
import sources.general as T_GEN

cogName = "Retrieval Cog"
cogDescription = "This part of the bot aids in finding stories and other story-related utilities."

_listText = lambda item, joinedItems, suffix=True: f"Below is each valid {item}: ```\n{joinedItems}```" + "" if not suffix else "\nIf your {item} is not listed here, please let {G.mentionMe} or a moderator know."
listGenre = _listText("genre", "\n".join(ALL_GENRES))
listSiteAbbrs = _listText("site abbreviation", "\n".join([f"{name} (used for {ALL_SITE_ABBREVIATIONS[name]})" for name in ALL_SITE_ABBREVIATIONS]))
listRatings = _listText("rating", ", ".join(ALL_RATINGS), False)

errorRandomStoryFail = "Couldn't find a story."

embedSearchAuthorTitle = lambda name: f"Stories by {name}"
embedSearchAuthorDescription = lambda jump, name: f"Archive post:\n{jump}" if jump else f"{name} doesn't have any posts in the story archive."

embedGuideTitle = "Archive guide"
embedGuideDescription = """ This embed will tell you how to set up a story in story-links.

All of these commands must happen in the story-links channel - they won't work anywhere else.

To start, use the `lap.addstory` command to add a new story, and give it your story's name in quotes.
```lap.addstory "Null Protocol"```

Next, you may use the `lap.addgenre` command to give your story a genre - these can be found using the command `lap.listgenres`. You can use this multiple times to add multiple genres to your story. Since these are all single-word, no quotes are necessary.
```lap.addgenre Adventure
lap.addgenre Friendship```

To add a rating to your story, use the `lap.setrating` command. Possible ratings can be found using the command `lap.listratings`.
```lap.setrating T```

If you want, you may add a reason why you rated your story the way you did with the `lap.setratingreason` command. This can be anything and can include spoilers if you wish. Note that the reason must be surrounded in quotes.
```lap.setratingreason "Swearing, ||graphic depictions of violence||"```

Multiple characters can be added to your story through the `lap.addcharacter` command. Give it a species followed by a name (if applicable / wanted). If a species or name has spaces in it, you will need to surround it in quotes, otherwise this is not necessary. If you give both a species and a name, it will appear in the post the opposite way (e.g. "Orial | Mienfoo"). Also note that the order in which the characters are added determines the order in which they appear in the post.
```lap.addcharacter Cyndaquil Quil
lap.addcharacter Mienfoo Orial
lap.addcharacter Yveltal "The Living God"```

Next you can add a summary to your story with the `lap.setsummary` command. Note that the summary must be surrounded in quotes.
```lap.setsummary "Forterra has been swept by the new pandemic mystery dungeons... etc."```

Last in the list is the links, which can be added using the `lap.addlink` command. It takes a name for the link and the link itself. The list of valid link names can be found using the `lap.listlinknames` command.
```lap.addlink AO3 https://archiveofourown.org/``` """
