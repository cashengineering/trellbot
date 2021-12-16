import os
import sys
import re
import discord
import safer
import pickle
import custom_errors

from discord.ext import commands
from dotenv import load_dotenv

#Dotenv Section (Private Variables stored in .env)
load_dotenv()

#Discord Variables
COMMAND_START = os.getenv('COMMAND_START')

guildList = []

class GuildData():

    def __init__(self, ID, name):
        self.ID = ID
        self.name = name
        self.permissions = 0
        self.boardGUIDList = []
        self.activeBoardGUID = ""

#Guild Data

def guildBoolean(guildID_Input):
    #TODO: Scrap this Function and Use "IN" instead
    #TODO: Write Docstring, Rename Function
    for x in range(len(guildList)):
        if (guildList[x].ID == guildID_Input):
            return True
    return False


def guildIndex(guildID_Input):
    for x in range(len(guildList)):
        if (guildList[x].ID == guildID_Input):
            return x
    return -1

def createGuildData(guildID_Input, guildName_Input):
    guildList.append(GuildData(guildID_Input, guildName_Input))

def commandCleanup(message):
    """
    This Function returns the non-command content for a messsage using
    regex. If there is no non-command content, None is returned.
    """

    regexSearchString = r""+"\\" + COMMAND_START + ".*?\s"+""
    regexMatches = re.search(regexSearchString, message)
    if regexMatches:
        return message[regexMatches.end()::]
    else:
        return None



#TODO: Call this function perodically to stop data loss
def saveAllGuildData():
    try:
        with safer.open('guildData.txt', 'wb') as outputFile:
            pickle.dump(guildList, outputFile)
        print("Guild Data Saved Successfully")
        return True

    except:
        print("Bot Unable to Save Data:", sys.exc_info()[0])
        return False



def loadAllGuildData():
    #TODO: This should probably not use True and False Returns
    try:
        with safer.open('guildData.txt', 'rb') as inputFile:
            loadedGuildData = pickle.load(inputFile)
            print("Guild Data Loaded Successfully")
            for x in range (len(loadedGuildData)):
                guildList.append(loadedGuildData[x])

            return True

    except:
        if(os.path.isfile("guildData.txt") == False):
            os.mknod("guildData.txt")
            print("The No -guildData.txt- File Detected:"+
                  "\nThis File Has Been Created")
            return False

        else:
            print("Bot Unable to Load Data:", sys.exc_info()[0])
            return False
