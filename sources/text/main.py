
from sources.general import BOT_PREFIX, MENTION_ME

presence = f"{BOT_PREFIX}help"

missingRequiredArgument = lambda param: f"You missed an argument that is required to use this command: {param}"
tooManyArguments = "You gave this command too many arguments. Make sure you're surrounding arguments that have spaces in them with quotes (space is the delimiter for arguments)."
commandInvokeError = "Something went wrong when invoking this command. Check how many arguments you have (and remember to surround arguments containing spaces with quotes)."
commandNotFound = "This command doesn't exist!"
commandOnCooldown = lambda wait: f"This command is on cooldown right now. Please wait {wait} seconds and try again."
invalidEndOfQuotedStringError = f"You have extra characters after your quoted argument."

unexpected = f"An unexpected error occurred. Please let {MENTION_ME} know."
