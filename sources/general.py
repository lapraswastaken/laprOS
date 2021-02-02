
import sources.ids as IDS

LAPROS_GRAPHIC_URL = "https://cdn.discordapp.com/attachments/284520081700945921/799416249738067978/laprOS_logo.png"

MENTION_ME = f"<@{IDS.MY_USER_ID}>"
BOT_PREFIX = "lap."
EMPTY = "\u200b"

REF_COMMAND = lambda command: f'`{BOT_PREFIX}{command["name"]}`'
REF_COMMAND_PLAIN = lambda command: f'{BOT_PREFIX}{command["name"]}'
