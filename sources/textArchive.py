
MAX_TITLE_LEN = 50
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

firstEmoji = "⏪"
priorEmoji = "⬅"
nextEmoji = "➡"
lastEmoji = "⏩"

errorNotInArchiveChannel = "This part of the bot can only be used in the channel that hosts story links."

messageWait = "Please wait..."
messagePrefix = "**Writer**:"
messageBody = lambda authorID, formattedStory: f"{messagePrefix} <@{authorID}>\n\n{formattedStory}\n\n====="
embedTitle = "Stories"
embedDescription = lambda formattedPost: formattedPost

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
