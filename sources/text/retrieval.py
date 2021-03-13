
import sources.text.archive as ARCH
from sources.general import ALL_GENRES, ALL_RATINGS, ALL_SITE_ABBREVIATIONS, BOT_PREFIX as lap, Cmd, MENTION_ME, NEWLINE, stripLines

cog = {
    "name": "Retrieval Cog",
    "description": "This part of the bot aids in finding stories and has other story-related utilities."
}

setArchiveChannel = Cmd(
    "setarchivechannel",
    "Sets the archive channel for this server.",
    usage = [
        "story-links",
        "792629600860897330",
        "<#792629600860897330>"
    ],
    success = lambda channel: f"Successfully set the archive channel to `{channel}`."
)
useHere = Cmd(
    "usehere",
    f"Sets the story archive to use when operating the bot in DMs to the one for the guild in which the command is being issued.",
    errorDM = "This command can't be used in direct messages.",
    success = lambda guild: f"Successfully set your archive preference to the story archive in `{guild}`."
)
whichArchive = Cmd(
    "whicharchive", "whichguild",
    f"""
        Gets the story archive you will use when using the bot in direct messages.
    """,
    success = lambda guild: f"In direct messages, you're currently set to use the archive in `{guild}`."
)

clearProxy = Cmd(
    "clearproxy",
    f"Clears the issuer's proxy and allows them to use the {ARCH.cogName} normally.",
    success = lambda user: f"You are no longer proxying the user `{user}`."
)
proxy = Cmd(
    "proxy", "proxyuser",
    f"Allows the issuer to edit stories by another user, specified via mention, name, or user ID. While proxying a user, any {ARCH.cogName} commands used to alter a post will be carried out as if the issuer was that user. Use `{clearProxy.name}` to stop proxying a user.",
    usage = [
        "laprOS",
        "785222129061986304",
        "<@785222129061986304>"
    ],
    selfProxy = f"You can't proxy yourself.",
    success = lambda user: f"You are now proxying the user `{user}`."
)
noProxy = "You are not currently proxying any users."
getProxy = Cmd(
    "getproxy", "proxyget",
    f"""
        Gets the user that the issuer is currently proxying.
    """,
    proxy = lambda user: f"You are currently proxying `{user}`."
)
dmMe = Cmd(
    "dmme", "dm",
    f"""
        Sends the issuer a direct message.
        Can be used to start adding/editing a story post in direct messages.
    """,
    success = f"If you intend to use the {ARCH.cogName}'s commands here, please make sure you are using the guild with the archive you would like to add to / edit in using the {whichArchive.refF} command, and if not, use the {useHere.refF} command in that guild to do so."
)
_listText = lambda item, joinedItems, suffix=True: f"Below is each valid {item}: ```\n{joinedItems}```" + ("" if not suffix else f"\nIf your {item} is not listed here, please let a moderator know.")
listGenres = Cmd(
    "listgenres",
    f"Gets a list of possible story genres to be added with {ARCH.addGenre.refF}.",
    success = _listText("genre", "\n".join(ALL_GENRES))
)
listSites = Cmd(
    "listsites",
    f"Gets a list of valid site abbreviations to be used with {ARCH.addLink.refF}.",
    success = _listText("site abbreviation", "\n".join([f"{name} (used for {ALL_SITE_ABBREVIATIONS[name]})" for name in ALL_SITE_ABBREVIATIONS]))
)
listRatings = Cmd(
    "listratings",
    f"Gets a list of valid ratings to be set with {ARCH.setRating.refF}.",
    success = _listText("rating", ", ".join(ALL_RATINGS), False)
)
archiveGuide = Cmd(
    "archiveguide", "archivehelp",
    f"Shows a help message that explains how to add a story through the {ARCH.cogName}.",
    pages = [
        {
            "title": "Archive Guide",
            "description": f"""
                The main feature of this bot is its story archive. In the archive, stories are displayed in a neat uniform fashion and can be fetched using various search commands. This guide will tell you how to set up a post in your server's archive channel.
                
                Commands used in this guide must either be used in your server's archive channel or in direct messages with the bot. To use the commands in direct messages, you must first select the Discord server you want to add a post to via the {useHere.refF} command.
            """
        },
        {
            "title": "Multi and Other Information",
            "description": f"""
                Before we begin, make sure you use the {ARCH.multi.refF} command if you want to perform multiple commands in one go. It's possible to add all the info for a story in one fell swoop, but only if you use this command. Use `{lap}help {ARCH.multi.name}` for more information.
                
                Also, if you run into a length limit for any of your story info and want to get around it, you may ask one of the moderators for assistance.
            """
        },
        {
            "title": "Adding / Removing a Story, Changing Titles",
            "description": f"""
                Use the {ARCH.addStory.refF} command to add a new story, and give it your story's name.
                ```{ARCH.addStory.ref} Null Protocol```
                
                If you want to remove any of your stories, you may use the {ARCH.removeStory.refF} command and give it the target story's name.
                ```{ARCH.removeStory.ref} Null Protocol```
                
                If you want to alter a story's name, focus that story in your post and use the {ARCH.setTitle.refF} command.
                ```{ARCH.setTitle.ref} Pokemon Mystery Dungeon: Null Protocol```
            """
        },
        {
            "title": "Adding / Removing Genres",
            "description": f"""
                Use the {ARCH.addGenre.refF} command to give your story a genre. Valid genres can be found using the command {listGenres.refF}. If you want to add multiple genres at a time, separate each with a space.
                ```{ARCH.addGenre.ref} Adventure Friendship```
                
                If you want to remove genres from a story, focus that story in your post and use the {ARCH.removeGenre.refF} command. You may remove multiple genres at a time by separating each with a space.
                ```{ARCH.removeGenre.ref} Adventure Friendship```
            """
        },
        {
            "title": "Adding a Rating",
            "description": f"""
                Use the {ARCH.setRating.refF} command to set the rating for your story. Valid ratings can be found using the command {listRatings.refF}.
                ```{ARCH.setRating.ref} T```
            """
        },
        {
            "title": "Adding a Rating Reason",
            "description": f"""
                Use the {ARCH.setRatingReason.refF} command to add a little blurb next to your rating describing why you rated your story the way you did. Note that you can use spoilers in this blurb.
                ```{ARCH.setRatingReason.ref} Swearing, violence, ||character death||.```
            """
        },
        {
            "title": "Adding / Removing Characters",
            "description": f"""
                Use the {ARCH.addCharacter.refF} command to add characters to your story. Characters have a species and an optional name. If your character doesn't have/need a name, you can simply enter their species. If your character needs both a species and a name, give their name followed by a comma followed by their species. See the examples below.
                ```{ARCH.addCharacter.ref} Quil, Cyndaquil
                {ARCH.addCharacter.ref} Orial, Mienfoo
                {ARCH.addCharacter.ref} Guildmaster Kess, Archeops
                {ARCH.addCharacter.ref} Yveltal```
                
                If you wish to remove a character from your story, use the {ARCH.removeCharacter.refF} command. If the target character has a unique species among all of your characters, you may enter their species. Otherwise you will need to give the name and the species of the target character with the above formatting.
                ```{ARCH.removeCharacter.ref} Quil, Cyndaquil
                {ARCH.removeCharacter.ref} Orial, Mienfoo
                {ARCH.removeCharacter.ref} Guildmaster Kess, Archeops
                {ARCH.removeCharacter.ref} Yveltal```
            """
        },
        {
            "title": "Adding a Summary",
            "description": f"""
                Use the {ARCH.setSummary.refF} command to set the summary for your story. If you want to use newlines in this summary, you will have to surround it in quotes.
                ```{ARCH.setSummary.ref} Forterra has been swept by the new pandemic mystery dungeons... (etc.)```
            """
        },
        {
            "title": "Adding / Removing Links",
            "description": f"""
                Use the {ARCH.addLink.refF} command to add links to your story. This command takes the abbreviation for the site and the URL itself. The list of valid site abbreviations can be found using the {listSites.refF} command.
                ```{ARCH.addLink.ref} AO3 https://archiveofourown.org/```
                
                If you want to remove a link from your story, use the {ARCH.removeLink.refF} command and give it the site abbreviation for the target link.
                ```{ARCH.removeLink.ref} AO3```
            """
        }
    ]
)
fetch = Cmd(
    "fetch", "search", "f", "s",
    f"A parent command for various search functions. Use `{lap}help fetch` for more information.",
    noArgs = f"This command gives various ways to search for stories in the story archive. Use `{lap}help fetch` for more information.",
    error = lambda entry: f"{entry} is an invalid subcommand."
)
byRandom = Cmd(
    "random", "r",
    f"Fetches a post at random from the story archive.",
    parent=fetch,
    error = "Couldn't find a story.",
    embed = lambda title, author, summary, jumpURL: {
        "title": title,
        "description": f"""
            by {(author + NEWLINE) + (f"```{summary}```" if summary else "No description")}
            
            {jumpURL}
        """
    }
)

noPost = lambda author: f"`{author}` doesn't have a post in the story archive for this server."
deletedPost = lambda author: f"`{author}`'s post's message was removed somehow and can't be displayed. Ask {MENTION_ME} for help."
byAuthor = Cmd(
    "author", "a",
    f"Fetches the post created by the given author from the story archive. The entry must be an exact username, a mention, or a user ID.",
    usage=[
        "lapras",
        "@lapras",
        "194537964657704960"
    ],
    parent=fetch,
    embed = lambda author, stories, jumpURL: {
        "title": f"Stories by {author}",
        "description": f"""
            > {(NEWLINE + '> ').join(stories)}
            
            {jumpURL}
        """
    }
)
collectionEmbed = lambda target, author, stories, jumpURL: {
    "title": f"{author}'s results for {target}",
    "description": f"""
        > {(NEWLINE + '> ').join(stories)}
        
        {jumpURL}
    """
}
byTitle = Cmd(
    "title", "t",
    f"Gets all of the stories whose title contains the command's entry. Organizes by post.",
    usage=[
        "Null Protocol",
        "Protocol"
    ],
    parent=fetch,
    noResults = lambda target: f"There were no results for stories with the title `{target}`."
)
bySpecies = Cmd(
    "species", "s",
    f"Gets all of the stories that feature a character of the entered species. Organizes by post.",
    usage=[
        "porygon",
        "Porygon Z"
    ],
    parent=fetch,
    noResults = lambda target: f"There were no results for stories with a `{target}` character."
)
byGenre = Cmd(
    "genre", "g",
    f"Gets all of the stories that are marked with the entered genre. Organizes by post.",
    usage=[
        "adventure",
        "Friendship"
    ],
    parent=fetch,
    noResults = lambda target: f"There were no results for stories with the `{target}` genre."
)