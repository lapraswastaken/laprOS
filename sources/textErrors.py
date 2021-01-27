
import sources.general as T_GEN

missingRequiredArgument = lambda param: f"You missed an argument that is required to use this command: {param}"
tooManyArguments = "You gave this command too many arguments. Make sure you're surrounding arguments that have spaces in them with quotes (space is the delimiter for arguments)."
commandNotFound = "This command doesn't exist!"
commandOnCooldown = lambda wait: f"This command is on cooldown right now. Please wait {wait} seconds and try again."
invalidEndOfQuotedStringError = f"You have extra characters after your quoted argument."

unexpected = f"An unexpected error occurred. Please let {T_GEN.mentionMe} know."

dmMessage = lambda text: f"There was an error with your command:\n```\n{text}\n```"
dmMessageWithChannel = lambda command, channelID, text: f"There was an error with your command `{command}` in the channel <#{channelID}>:\n```\n{text}\n```"
