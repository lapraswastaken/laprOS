
MAX_TITLE_LEN = 75
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

cogName = "Archive Cog"
cogDescription = "This part of the bot handles the addition, removal, and editing of stories to the story archive. All commands here must be used in your server's dedicated archive channel. For a walkthrough on how to add your story, use the Retrieval Cog's `archiveguide` command."

class cmd:
    clearProxy = {
        "name": "clearproxy",
        "help": f"Clears the issuer's proxy and allows them to use the {cogName} normally."
    }
    proxyUser = {
        "name": "proxyuser",
        "help": f"Allows the issuer to edit stories by another user, specified via mention or user ID. While proxying a user, any {cogName} commands used to alter a post will be carried out as if the issuer was that user. Use `" + clearProxy["name"] + "` to stop proxying a user."
    }
    multi = {
        "name": "multi",
        "help": "Performs multiple commands (split apart by newlines) at once. Big thanks to love for laying the groundwork for this command."
    }
    addStory = {
        "name": "addstory",
        "help": "Adds a new story with the given title to the issuer's archive post, creating a post if none exists for them."
    }
    removeStory = {
        "name": "removestory",
        "help": "Removes the story with the given title from the issuer's archive post. BE WARNED - This can't be undone. "
    }
    _theStorySuffix = ""
    setTitle = {
        "name": "settitle",
        "help": f"Sets the title of the story currently focused in the issuer's archive post.\nThe entry must be under {MAX_TITLE_LEN} characters long."
    }
    addGenre = {
        "name": "addgenre",
        "aliases": ["addgenres", "setgenre", "setgenres"],
        "help": f"Adds one or more genres to the story currently focused in the issuer's archive post.\nEach entry must be a valid genre."
    }
    removeGenre = {
        "name": "removegenre",
        "aliases": ["removegenres"],
        "help": f"Removes one or more genres from the story currently focused in the issuer's archive post."
    }
    setRating = {
        "name": "setrating",
        "aliases": ["addrating"],
        "help": f"Sets the rating for the story currently focused in the issuer's archive post.\nThe entry must be a valid rating."
    }
    setRatingReason = {
        "name": "setratingreason",
        "aliases": ["addratingreason"],
        "help": f"Sets the rating reason for the story currently focused in the issuer's archive post.\nThe entry must be less than {MAX_RATING_REASON_LEN} characters long and can include spoilers."
    }
    _characterFormattingText = "To specify a name and a species rather than just a species, use the format: `name` | `species` where `name` is the desired name for the character and `species` is the desired species."
    addCharacter = {
        "name": "addcharacter",
        "aliases": ["addchar", "setcharacter", "setchar"],
        "help": f"Adds a character with the given species to the story currently focused in the issuer's archive post.\n{_characterFormattingText}\nThe entry for the species of the character must be less than {MAX_CHAR_SPECIES_LEN} characters long. The entry for the name of the character, if desired, must be less than {MAX_CHAR_NAME_LEN} characters long."
    }
    removeCharacter = {
        "name": "removecharacter",
        "aliases": ["removechar"],
        "help": f"Removes a character from the story currently focused in the issuer's archive post.\n{_characterFormattingText}"
    }
    setSummary = {
        "name": "setsummary",
        "aliases": ["addsummary"],
        "help": f"Sets the summary for the story currently focused in the issuer's archive post.\nIf newlines are required, the entry must be surrounded in quotes.\nThe entry must be less than {MAX_SUMMARY_LEN} characters long."
    }
    addLink = {
        "name": "addlink",
        "aliases": ["setlink"],
        "help": f"Adds a link to the story currently focused in the issuer's archive post.\nThe first entry must be a valid site abbreviation. The second entry must be the desired URL from that site.\nThe second entry must be less than {MAX_LINK_URL_LEN} characters long. If your link is longer than this limit, talk to a moderator."
    }
    removeLink = {
        "name": "removelink",
        "help": f"Removes the link with the given site abbreviation from the story currently focused in the issuer's archive post."
    }

firstEmoji = "⏪"
priorEmoji = "⬅"
nextEmoji = "➡"
lastEmoji = "⏩"

archivePostMessageWait = "Please wait..."
archivePostMessagePrefix = "**Writer**:"
archivePostMessageBody = lambda authorID, formattedStory: f"{archivePostMessagePrefix} <@{authorID}>\n\n{formattedStory}\n\n====="
archivePostEmbedTitle = "Stories"
archivePostEmbedDescription = lambda formattedPost: formattedPost

errorNotInArchiveChannel = "This part of the bot can only be used in the channel that hosts story links."

errorNoArchiveChannel = "This server does not have an archive channel set up. Ask a server moderator to use the `setarchivechannel` command."
errorNoPost = "You don't have a post in the archive channel on this server."
errorNoStory = lambda title: f"Couldn't find a story titled \"{title}\"."

errorNoGenre = lambda citedStory, targetGenre: f"Your story, {citedStory}, does not have the {targetGenre} genre."
errorNoChar = lambda citedStory, species, name: f"Your story, {citedStory}, does not have a character with the species {species}" + ("." if not name else f" and the name {name}.")
errorNoLink = lambda citedStory, abbr: f"Your story, {citedStory}, does not have a link with the site abbreviation {abbr}."

errorDupStory = lambda storyTitle: f"You already have a story titled \"{storyTitle}\"."
errorDupGenre = lambda citedStory, genre: f"Your story, {citedStory}, already has the {genre} genre."
errorDupChar = lambda citedStory, species, name: f"Your story, {citedStory}, already has a character with the species {species}" + ("." if not name else f" and the name {name}.")
errorDupLink = lambda citedStory, abbr: f"Your story, {citedStory}, already has a link with the site abbreviation {abbr}. Remove it with the `removelink` command to change it."

_maxLenErrorText = lambda tooLong, maxLen: f"That {tooLong} is too long. It must be shorter than {maxLen} characters long."
errorLenTitle = _maxLenErrorText("story title", MAX_TITLE_LEN)
errorLenReason = _maxLenErrorText("rating reason", MAX_RATING_REASON_LEN)
errorLenCharSpecies = _maxLenErrorText("character's species", MAX_CHAR_SPECIES_LEN)
errorLenCharName = _maxLenErrorText("character's name", MAX_CHAR_NAME_LEN)
errorLenSummary = _maxLenErrorText("summary", MAX_SUMMARY_LEN)
errorLenLinkURL = _maxLenErrorText("link URL", MAX_LINK_URL_LEN)

errorInvalidGenre = lambda genre: f"The genre specified ({genre}) is not one of the following:\n\n" + "\n".join(ALL_GENRES)
errorInvalidRating = lambda citedStory, rating: f"The rating for your story, {citedStory}, must be one of {ALL_RATINGS}, not {rating}."
errorInvalidLinkAbbr = lambda citedStory, abbr: f"The site abbreviation for the link you are trying to add to your story, {citedStory}, must be one of " + ", ".join(ALL_SITE_ABBREVIATIONS.keys()) + f", not {abbr}."

errorInvalidCommand = lambda commandName: f"Couldn't find a command named {commandName}. Did you mistype?\n\n"
errorNumberArgs = lambda commandName: f"There was an incorrect number of arguments for the command {commandName}.\n\n"

errorMultiQuotes = lambda command: f"There was an issue with the quotes in your command: `{command}`"

errorCharacterNoSpecies = f"There was no species specified for this character."
