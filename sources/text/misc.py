
from sources.general import BOT_PREFIX, Cmd


cogName = "Misc Cog"
cog = {
    "name": cogName,
    "description": "This part of the bot has random miscellaneous things that don't fit anywhere else."
}

emojiGreen = "🟢"
emojiRed = "🔴"

protectDemocracy = "laprOS will not allow Hermit to silence democracy."

ping = Cmd(
    "ping",
    "A test command.",
    pong = "Pong"
)
cat = Cmd(
    "cat",
    "Sends a cute cat picture to the chat. (Bugged for certain users.)",
    cat = lambda message: message
)
vote = Cmd(
    "vote",
    "Starts a vote on this command's message.",
    emojiNotFound = f"Couldn't find one of the emojis you're trying to use for the vote. Are you sure it's available on this server?"
)
coinflip = Cmd(
    "coinflip", "flipcoin",
    "Performs a coinflip, heads or tails.",
    heads = "Heads!",
    tails = "Tails!"
)
addSpamChannel = Cmd(
    "addspamchannel",
    "Registers a channel to allow the use of spam commands.",
    success = lambda channel: f"Successfully added channel {channel} to the list of spam command channels.",
    duplicate = lambda channel: f"The channel {channel} is already listed as a spam command channel."
)
removeSpamChannel = Cmd(
    "removespamchannel",
    "Removes a channel from the list of spam command channels.",
    success = lambda channel: f"Successfully removed channel {channel} from the list of spam command channels.",
    notFound = lambda channel: f"The channel {channel} is not listed as a spam command channel."
)
sup = Cmd(
    "sup",
    "Yo.",
    sup = "sup"
)
stab = Cmd(
    "stab",
    "Idfk, blame DragonD",
    usage=[
        "slink"
    ]
)
hug = Cmd(
    "hug",
    "Idfk, blame Bonehead",
    usage=[
        "",
        "lapras 🙂"
    ]
)
punch = Cmd(
    "punch",
    "Idfk, blame Sudmensch",
    usage=[
        "robbie"
    ]
)
dab = Cmd(
    "dab",
    "Idfk, blame Domingize",
    usage=[
        "",
        "on laprOS"
    ]
)
pizza = Cmd(
    "pizza",
    "Idfk, blame all yourselves because you voted for Hermit"
)

_TZ_GUIDE = "A valid time zone is something like `America/Chicago`. It's advised not to use abbreviations like EST, since those don't account for daylight savings time and one abbreviation can represent multiple time zones. For a list of valid timezones, check the entries of the \"TZ database name\" column on this Wikipedia page: <https://en.wikipedia.org/wiki/List_of_tz_database_time_zones>."
TIMEZONE = Cmd(
    "timezone", "tz",
    f"""
        If used on its own, gets the time zone you're currently using. Otherwise, sets your current time zone.
        {_TZ_GUIDE}
    """,
    usage=[
        "US/Eastern",
        "us/central",
        "america/detroit"
    ]
)
NOW = Cmd(
    "now",
    f"""
        Gets the current time based on your time zone.
    """
)
WHEN = Cmd(
    "when", "astimezone", "astz"
    f"""
        Translates a time to another timezone.
    """,
    usage=[
        "4:00pm US/Eastern",
        "14:00 america/detroit"
    ]
)

class INFO:
    TZ_USE_THIS = "Use this command to set your time zone. " + _TZ_GUIDE
    TZ_USING = lambda zone: f"You are currently using `{zone}` time."
    TZ_SUCCESS = lambda zone: f"Successfully set your timezone to `{zone}`."
    NOW = lambda zone, time: f"`{zone}` time is currently {time}."
    WHEN = lambda time1, timezone1, time2, timezone2: f"`{time1}` in {timezone1} is `{time2}` in {timezone2}."

class PATH:
    TZPREFS = "./sources/tzprefs.json"

class ERR:
    NO_TZ = f"You haven't set a timezone preference with {TIMEZONE.refF} yet."
    INVALID_TZ = lambda tz: f"{tz} is not a valid time zone. For help, use `{BOT_PREFIX}help {TIMEZONE.name}`."
    TIME_FORMAT = lambda time: f"The time `{time}` isn't correctly formatted. Try something like `12:00pm` or `15:00`."