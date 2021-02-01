
from typing import Optional
import discord
from discord.ext import commands
import sources.ids as IDS
import sources.textMisc as MISC

class MiniEntry:
    def __init__(self, userID: int, targetUserID: int, count: int):
        self.userID = userID
        self.targetUserID = targetUserID
        self.count = count

class CogMod(commands.Cog):
    def __init__(self):
        self.oldDeleteEntries: dict[int, MiniEntry] = {}
    
    @staticmethod
    async def getNewEntries(guild: discord.Guild) -> dict[int, MiniEntry]:
        
        timeout = 300
        newDeleteEntries: dict[int, MiniEntry]  = {}
        entry: discord.AuditLogEntry
        async for entry in guild.audit_logs():
            timeout -= 1
            if timeout <= 0:
                break
            if not entry.action == discord.AuditLogAction.message_delete: continue
            
            newDeleteEntries[entry.id] = MiniEntry(entry.user.id, entry.target.id, entry.extra.count)
        
        return newDeleteEntries
    
    async def handleOnReady(self, guild: discord.Guild):
        self.oldDeleteEntries = await CogMod.getNewEntries(guild)
    
    async def handleMessageDelete(self, message: discord.Message):
        if not message.guild.id in IDS.logChannelIDs: return
        
        newDeleteEntries = await CogMod.getNewEntries(message.guild)
        
        retrievedDeleterID: Optional[int] = None
        for newID in newDeleteEntries:
            newEntry = newDeleteEntries[newID]
            if not newEntry.targetUserID == message.author.id: continue
            
            if newID in self.oldDeleteEntries:
                oldEntry = self.oldDeleteEntries[newID]
                if newEntry.count == oldEntry.count + 1:
                    retrievedDeleterID = newEntry.userID
                    break
            else:
                retrievedDeleterID = newEntry.userID
                break
        if retrievedDeleterID != None:
            deleter: discord.Member = await message.guild.fetch_member(retrievedDeleterID)
            #if message.guild.id == 546872429621018635 and not 550518609714348034 in [role.id for role in deleter.roles]: return
            
            channel: discord.TextChannel = message.guild.get_channel(IDS.logChannelIDs[message.guild.id])
            await channel.send(MISC.deletedMessageText(message.author.id, deleter.id))
            await channel.send(
                message.content,
                embed=message.embeds[0] if message.embeds else None,
                files=[await attachment.to_file(use_cached=True) for attachment in message.attachments]
            )
        self.oldDeleteEntries = newDeleteEntries
