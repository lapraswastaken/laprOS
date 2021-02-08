
dmMessage = lambda text: f"There was an error with your command:\n```\n{text}\n```"
dmMessageWithChannel = lambda command, channelID, text: f"There was an error with your command ```\n{command}```in the channel <#{channelID}>:\n\n{text}\n"

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

indices = [emoji1, emoji2, emoji3, emoji4, emoji5, emoji6, emoji7, emoji8, emoji9, emoji10]

paginationIndex = lambda index, length: f"Page {index} of {length}."
