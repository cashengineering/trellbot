import discord

from discord.ext import commands

#Custom Exceptions

class GlobalCheckFailure(commands.CheckFailure):
    pass

class NotAdminGuild(commands.CheckFailure):
    pass

class NullMessage(commands.CheckFailure):
    pass
