
from sources.general import BOT_PREFIX, NEWLINE

cogEmbed = lambda cogName, cogDescription, commandNames: {
    "title": cogName,
    "description": f"""
        {cogDescription}
        
        Use `lap.help commandName` to get help with a specific command.
        ```
        {NEWLINE.join(commandNames)}```
    """
}

commandEmbed = lambda cmdName, cmdAliases, cmdDesc, cogName: {
    "title": f"`{BOT_PREFIX}{cmdName}`",
    "description": f"""
        {("also `" + "`, `".join(cmdAliases) + "`") if cmdAliases else ""}
        
        {cmdDesc}
    """,
    "footer": f"This command is a part of the {cogName}."
}

cogMessage = lambda cogName: f"**Commands for `{cogName}`**"
groupMessage = lambda groupName: f"**Commands for group `{groupName}`**"
