import nextcord
from nextcord.ext import commands
from nextcord import Interaction
from apikeys import *
import requests
import json

import mysql.connector
from mysql.connector import Error

# Database login details:
HOST = 'localhost'
DATABASE = 'jerma985bot'
USER = 'root'
PASSWORD = 'root'

# function to store currency into database
# serverID should be id of guild (interaction.guild.id)
# user should be the user object (interaction.user)
def storeData(serverID, user, data):
    connected = False;
    try:
        # create connection to sql server
        connection = mysql.connector.connect(host=HOST,
                                             database = DATABASE,
                                             user = USER,
                                             password = PASSWORD)
        connected = True;
        
        # create a table for the data (will error if it already exists)
        mySql_Create_Table_Query = """CREATE TABLE DB_""" + str(serverID) + """ (
                                 Id int(11) NOT NULL AUTO_INCREMENT,
                                 User varchar(250) NOT NULL,
                                 Currency varchar(500) NOT NULL,
                                 PRIMARY KEY (Id)) """
        cursor = connection.cursor()
        result = cursor.execute(mySql_Create_Table_Query)
        print("Server (" + str(serverID) + ") Table created successfully")
    
    # table already exists
    except mysql.connector.Error as error:
        print("Failed to create table in MySql: {}".format(error))
    
    finally:
        # insert data into database
        if connected and connection.is_connected():
            
            # setup variables
            table = "DB_" + str(serverID)
            MySql_Insert_Row_Query = "INSERT INTO " + table + " (User, Currency) VALUES (%s, %s)"
            MySql_Insert_Row_values = (str(user), data)

            # insert data
            cursor.execute(MySql_Insert_Row_Query, MySql_Insert_Row_values)
            connection.commit()                

            #close connections
            cursor.close()
            connection.close()
            print("MySQL connection has been closed")
            return True
        else:
            print("Failed to connect to database")
            return False
    
    
        

class Data(commands.Cog) :
    # ----------initialize cog----------
    def __init__(self, bot: commands.Bot) :
        self.bot = bot

    serverId = 1033811091828002817

    @commands.Cog.listener()
    async def on_ready(self):
        print("Data Cog Loaded")
    #   ----------done----------   


    @nextcord.slash_command(name = "store-info", description = "Store some data", guild_ids = [serverId])
    async def store_info (self, interaction : Interaction, message:str):
        serverID = interaction.guild.id

        success = storeData(serverID, interaction.user, message)
        if success:
            await interaction.response.send_message("I have stored your message for you!")
        else:
            await interaction.response.send_message("Uh oh! I'm having trouble connecting right now.")
        
        



# export cog to bot
def setup(bot: commands.Bot) :
    bot.add_cog(Data(bot))