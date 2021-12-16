import os
import sys
import re
import discord
import custom_errors

from custom_errors import *
from guildtools import *
from discord.ext import commands
from dotenv import load_dotenv
from trello import TrelloClient


#Dotenv Section (Private Variables stored in .env)
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
COMMAND_START = os.getenv('COMMAND_START')
ADMIN_GUILD_ID = int(os.getenv('ADMIN_GUILD_ID'))

#This Initializes The Bot
bot = commands.Bot(command_prefix=COMMAND_START)

#Trello Variables
API_KEY = os.getenv('TRELLO_API_KEY')
API_SECRET  =  os.getenv('TRELLO_API_SECRET')
OAUTH_TOKEN = os.getenv('TRELLO_OAUTH_TOKEN')
OAUTH_SECRET = os.getenv('TRELLO_OAUTH_SECRET')

trello_client = TrelloClient(
    api_key=API_KEY,
    api_secret=API_SECRET,
    token=OAUTH_TOKEN,
    token_secret=OAUTH_SECRET)


# Checks and Error Handling

def check_commands(ctx):
    """
    This Global Check ensures that no commands are processed that are:
    Not from the Trello Channel, From A Bot User, From The Bot Itself, or
    From A Cog That Already Has Its Own "cog.check" occurring.
    """

    message = ctx.message
    if message.channel.name == 'trello':
        if message.author != bot.user or not message.author.bot:
            if not hasattr(ctx.command.cog, 'Cog.cog_check'):
                return True

    raise GlobalCheckFailure()



def checkNullMessage():
    #This Check Will See If The Non-Command Contents of a Message Is Null
    #If so, raise the appropriate error.

    def predicate(ctx):
        if (commandCleanup(ctx.message.content) == None):
            raise NullMessage()

        else:
            return True

    return commands.check(predicate)


@bot.listen()
async def on_command_error(ctx, error):
    """
    This function is the global error handler.
    If an error occurs checks are made to see if the error was custom error.
    If the error was not specifically handled, a message is printed out.
    """

    #This Prevents Local Error Handlers From Being Handled Here
    if hasattr(ctx.command, 'on_error'):
        return

    if isinstance(error, GlobalCheckFailure):
        return

    if isinstance(error, NotAdminGuild):
        return

    if isinstance(error, NullMessage):
        await ctx.message.channel.send("This Command Requires An Input.")
        return

    print("\nUnknown Error:\n", error)



#Cogs and Bot Code

class AdminCog(commands.Cog):
    """
    This Cog contains all of the Administrative commands.
    TODO: Actually write this Docstring
    """

    def __init__(self, bot):
        self.bot = bot

    #Listener to see if the message originated from the Admin Guild
    async def cog_check(self, ctx):

        #Admin Commands Originating From The ADMIN_GUILD can come from a bot.
        if ctx.message.channel.name != 'trello':
            if ctx.message.guild.id != ADMIN_GUILD_ID:
                raise NotAdminGuild()
            raise GlobalCheckFailure()

        else:
            print("Recieved An Admin Command From The Admin Guild.\n" +
                  "Executing The Following Command: " + ctx.message.content)
            return True



    #This checks for Admin permissions, and then closes the Bot
    @commands.command(aliases=["exit"])
    @commands.has_permissions(administrator=True)
    async def close(self, ctx):
        """
        This function closes the bot after saving data to
        the data file using the safer library.
        Upon failure this function prints an error message
        and the bot is not closed.
        """

        if(saveAllGuildData() == True):
            await bot.close()
            print("Bot Closed")

        else:
            print("Bot Unable To Close Due to Unwritten Data")



    @commands.command(aliases=["Force_Quit"])
    @commands.has_permissions(administrator=True)
    async def shutdown(self, ctx):
        """
        This function will forcibly close the bot without
        allowing it to save data.
        """

        print("Shutting Down the Bot Without Saving")
        await bot.close()



    @commands.command(aliases=["CLEAR_DATA"])
    @commands.has_permissions(administrator=True)
    async def clearGuildData(self, ctx):
        """
        This function clears all of the data currently stored in memory of the
        bot, and then repopulate it from scratch.
        This is useful for testing and for when the data within the bot
        needs to be updated as a result of the GuildData Class getting new
        variables.
        """

        global guildList
        guildList = []

        try:

            self.bot.boardDict = {}

            for x in range (len(bot.guilds)):
                createGuildData(bot.guilds[x].id, bot.guilds[x].name)
            print("Data Repopulated Successfully")

        except:
            print("Data Was Unable To Repopulate", sys.exc_info()[0])



class TrelloCog(commands.Cog):
    """
    This Cog contains commands necessary to integrate with the Trello API
    Note, your COMMAND_START Var may differ.
    To use:
    > !setboard <name_of_board>
    > ???
    > Profit!
    #TODO: Actually write this Docstring
    """

    def __init__(self, bot):
        self.bot = bot
        self.bot.boardDict = {}

    @commands.command()
    @checkNullMessage()
    async def addboard(self, ctx):
        """
        This function takes in a Trello URL/boardGUID, verifies it using
        regex, and then turns it into a boardGUID if it wasn't one already.
        If Trellbot can access the board and the guild isn't at its maximum
        boards or isn't already on the guild's boardGUIDList, the board is
        added to the list. If any of these three conditions is failed,
        an appropriate response is given.
        """

        #TODO: Add some sort of message telling the user how many boards this
        #      guild has left to add before it has reached its max

        command = commandCleanup(ctx.message.content)
        regexMatches = re.search(r"b\/.*?\/", command)
        guild = guildList[guildIndex(ctx.message.guild.id)]

        if regexMatches:
            boardGUID = command[regexMatches.start():regexMatches.end()]

            if (self.boardBoolean(boardGUID) == True):
                if (boardGUID in guild.boardGUIDList):
                    await ctx.message.channel.send("Board Already Exists "+
                                                    "In Server.")
                    return

                if (len(guild.boardGUIDList) <= 3):
                    guild.boardGUIDList.append(boardGUID)
                    await ctx.message.channel.send("Board Added Successfully!")
                    return

                else:
                    await ctx.message.channel.send("This Server Has Reached "+
                                                   "Its Board Limit.")

        else:
            await ctx.message.channel.send("No Board With That URL Could Be "+
                                           "Found.")



    @commands.command()
    async def getboards(self, ctx):
        """
        This function uses the Global Variable guildList which stores all
        instances of the GuildData class. This function grabs all of the
        boardGUIDList data, which are the Board Keys/Unique Identifiers in Trello URLS,
        turns them into full URLs and then throws them back at the user.
        """

        guild = guildList[guildIndex(ctx.message.guild.id)]
        boardGUIDList = guild.boardGUIDList
        returnMessage = ""

        for x in range (len(guild.boardGUIDList)):
            boardURL = self.boardGUIDToURL(boardGUIDList[x])
            returnMessage += boardURL + "\n"

        await ctx.message.channel.send("Current List of Boards:\n" + returnMessage)
        return



    @commands.has_permissions(administrator=True)
    @commands.command()
    @checkNullMessage()
    async def removeboard(self, ctx):
        """
        This function uses the same regex as the addboard command, which checks
        for the matching boardGUID String in a Given URL. Once the input
        boardGUID has been verified a check is made to be sure that the guild
        has access to this board. If true the board is then deleted from the
        guild's access. If the board is also the guild's active board the
        activeBoardGUID is reset, and the board's data is deleted from memory.
        """

        #TODO: Make this an administrator or admin command only
        #TODO: Add a Warning Message for users if they're trying to delete
        #      their active board.

        command = commandCleanup(ctx.message.content)
        regexMatches = re.search(r"b\/.*?\/", command)
        guild = guildList[guildIndex(ctx.message.guild.id)]
        returnMessage = ""

        if regexMatches:
            boardGUID = command[regexMatches.start():regexMatches.end()]
            if boardGUID in guild.boardGUIDList:
                boardGUIDIndex = guild.boardGUIDList.index(boardGUID)
                guild.boardGUIDList.pop(boardGUIDIndex)

                if (boardGUID == guild.activeBoardGUID):
                    guild.activeBoardGUID = ""
                    self.bot.boardDict.pop(guild.ID)

                returnMessage += "Board Successfully Removed."
                await ctx.message.channel.send(returnMessage)
                return

        await ctx.message.channel.send("No Board With That URL Could Be Found")
        return


    @commands.command()
    @checkNullMessage()
    async def setboard(self, ctx):
        """
        This function uses the guild's boardGUIDs, turns them into urls and
        then checks to see if the board name or url matches the command.
        If a match is found then create/edit an entry in the
        "self.bot.boardDict" using the guild's ID as they key and the
        returned board as an Entry. After this the guild's activeBoardGUID
        is set to the GUID of the guild's tracked board.
        """

        #TODO: Write a Check to see if the board is already what the user wants

        command = commandCleanup(ctx.message.content)
        guildID = ctx.message.guild.id
        guild = guildList[guildIndex(guildID)]

        for boardGUID in guild.boardGUIDList:
            url = self.boardGUIDToURL(boardGUID)
            regexMatches = re.search(r".*/", url)
            boardName = url[regexMatches.end()::].replace("-", " ")

            if (boardName.lower() == command.lower()) or (url == command):
                returnedBoard = self.getBoard(boardName)
                guild.activeBoardGUID = boardGUID
                self.bot.boardDict[guildID] = returnedBoard
                await ctx.message.channel.send("Board Successfully Set!")
                return

        await ctx.message.channel.send("This Guild Has No Access To A Board "+
                                       "Named \n" + command)



    @commands.command()
    async def getlists(self, ctx):
        """
        This function determines what board is being tracked by the Guild and
        then return a message of the lists in the given board. If there is no
        board that is being tracked, the bot will return an error message.
        """

        #TODO: Make this do Embed things
        self.loadBoard(ctx)

        if ctx.message.guild.id in self.bot.boardDict:
            board = self.bot.boardDict[ctx.message.guild.id]
            try:
                returnMessage = "Active Lists On This Board:\n"
                for tlist in board.all_lists():
                    if (tlist.closed != True):
                        returnMessage += tlist.name + "\n"
                await ctx.message.channel.send(returnMessage)
                return

            except:
                print("An Error Has Occurred:", sys.exc_info()[0])
                await ctx.message.channel.send("An Unknown Error Has Occurred.")
                return

        else:
            await ctx.message.channel.send("No Board detected - Please run 'setboard' first.")
            return

    @commands.command()
    @checkNullMessage()
    async def getcards(self, ctx):
        """ Prints out a list of every card in a given list """

        command = commandCleanup(ctx.message.content)
        self.loadBoard(ctx)

        #TODO: Make this do Embed things
        if ctx.message.guild.id in self.bot.boardDict:
            board = self.bot.boardDict[ctx.message.guild.id]

            try:
                returnMessage = "Active Cards on this List:\n"
                for tlist in board.all_lists():
                    if (tlist.closed != True) and (tlist.name.lower() == command.lower()):
                        for card in tlist.list_cards():
                            returnMessage += card.name + "\n"
                        await ctx.message.channel.send(returnMessage)
                        return

                await ctx.message.channel.send("No List Named \n"+
                                                command + "\n Could Be Found.")
                return

            except:
                print("An Error Has Occurred:", sys.exc_info()[0])
                await ctx.message.channel.send("An Unknown Error Has Occurred.")
                return

        else:
            await ctx.message.channel.send("No Board detected - Please run 'setboard' first.")



    @commands.command()
    async def embed(self, ctx):
        embed=discord.Embed(title="Title ~~(did you know you can have markdown here?)~~")
        embed.add_field(name="Field - x1", value="this `supports` __a__ **subset** *of* ~~markdown~~ 😃 ```js\nfunction foo(bar) {\n  console.log(bar);\n}\n\nfoo(1);```", inline=True)
        embed.add_field(name="Field - x2", value="this `supports` __a__ **subset** *of* ~~markdown~~ 😃 ```js\nfunction foo(bar) {\n  console.log(bar);\n}\n\nfoo(1);```", inline=True)
        embed.add_field(name="Field - x3", value="this `supports` __a__ **subset** *of* ~~markdown~~ 😃 ```js\nfunction foo(bar) {\n  console.log(bar);\n}\n\nfoo(1);```", inline=False)
        embed.set_footer(text="A footer")
        await ctx.message.channel.send(embed=embed)



    def getBoard(self, name_lookup):
        for board in trello_client.list_boards():
            if name_lookup.lower() == board.name.lower():
                return board
        return -1



    def boardGUIDToName(self, boardGUID):
        url = self.boardGUIDToURL(boardGUID)
        regexMatches = re.search(r".*/", url)
        boardName = url[regexMatches.end()::].replace("-", " ")
        return (boardName)



    def boardBoolean(self, boardGUID_lookup):
        # This function checks if Trellbot has access to a board using its boardGUID
        for board in trello_client.list_boards():
            if (board.url.find(boardGUID_lookup) != -1):
                return True
        return False



    def boardGUIDToURL(self, boardGUID):
        for board in trello_client.list_boards():
            if (board.url.find(boardGUID) != -1):
                return board.url



    def loadBoard(self, ctx):
        guild = guildList[guildIndex(ctx.message.guild.id)]
        boardGUID = guild.activeBoardGUID

        if (boardGUID != ""):
            if guild.ID not in self.bot.boardDict:
                board = self.getBoard(self.boardGUIDToName(boardGUID))
                self.bot.boardDict[guild.ID] = board




@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

    loadAllGuildData()

    #This Prints out all of the Current Guilds The Bot is Connected To
    print("\nCurrent Loaded Guilds List:")
    for x in range (len(guildList)):
        print(guildList[x].name, "Guild ID:", guildList[x].ID)
    print("---END---\n")

    for x in range (len(bot.guilds)):
        if (guildBoolean(bot.guilds[x].id) == False):
            print("New Guild Detected, Adding New Guild.")
            createGuildData(bot.guilds[x].id, bot.guilds[x].name)




if __name__ == "__main__":
    bot.add_cog(AdminCog(bot))
    bot.add_cog(TrelloCog(bot))
    bot.run(TOKEN)