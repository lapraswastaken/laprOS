
import sources.text.retrieval as RETR

dmMessage = lambda text: f"{text}"
dmMessageWithChannel = lambda command, channelID, text: f"{text}\n\n(error from your command ```\n{command}```in the channel <#{channelID}>)"

emojiFirst = "⏪"
emojiPrior = "⬅"
emojiNext = "➡"
emojiLast = "⏩"

emoji1 = "1️⃣"
emoji2 = "2️⃣"
emoji3 = "3️⃣"
emoji4 = "4️⃣"
emoji5 = "5️⃣"
emoji6 = "6️⃣"
emoji7 = "7️⃣"
emoji8 = "8️⃣"
emoji9 = "9️⃣"
emoji10 = "🔟"

emojiNumbers = "🔢"
emojiArrows = "↔️"

arrows = [emojiFirst, emojiPrior, emojiNext, emojiLast]
indices = [emoji1, emoji2, emoji3, emoji4, emoji5, emoji6, emoji7, emoji8, emoji9, emoji10]
switches = [emojiNumbers, emojiArrows]

paginationIndex = lambda index, length: f"Page {index} of {length}."

errorDMModCheck = "This command requires moderator priveleges, and therefore can't be used in direct messages."
errorNotMod = "This command requires moderator priveleges."

errorNotInArchiveChannel = "This part of the bot can only be used in the channel that hosts story links or a direct message channel with the bot."
errorNoArchiveChannel = lambda guild: f"The guild that you currently have selected, `{guild}`, does not have an archive channel set up. Ask a moderator to use the {RETR.setArchiveChannel.refF} command."
errorNoArchivePreference = f"You haven't set your archive preference yet. You can do so with the {RETR.useHere.refF} command in the guild that has the archive channel you wish to use."
errorNoGuildAccess = f"The bot doesn't have access to your preferred guild. Select a new preference using the {RETR.useHere.refF} command in the guild that has the archive channel you wish to use."

errorNoGuild = f"You can't use a member ID in direct messages. If you wish to look up a member, do so in the guild that member is a part of."
errorUserIDNotFound = lambda id: f"Couldn't find a user with the ID `{id}`."
