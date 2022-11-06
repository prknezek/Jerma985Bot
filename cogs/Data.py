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
# returns boolean: True if successful, False if unsuccessful
# serverID should be id of guild (interaction.guild.id)
# user should be the user object (interaction.user)
def storeData(serverID, user, data):
    
    # connect to database
    connected = False;
    try:
        # create connection to sql server
        connection = mysql.connector.connect(host=HOST,
                                             database = DATABASE,
                                             user = USER,
                                             password = PASSWORD)
        connected = True;
    except:
        print("Failed to connect to database")
        return False
    
    # create a table if not already done
    try:    
        # create a table for the data (will error if it already exists)
        mySql_Create_Table_Query = """CREATE TABLE DB_""" + str(serverID) + """ (
                                 UserId bigint NOT NULL,
                                 UserStr varchar(250) NOT NULL,
                                 Currency varchar(500) NOT NULL,
                                 PRIMARY KEY (UserId)) """
        cursor = connection.cursor()
        result = cursor.execute(mySql_Create_Table_Query)
        print("Server (" + str(serverID) + ") Table created successfully")
    except mysql.connector.Error as error:
        print("Failed to create table in MySql: {}".format(error))
    
    # insert data into database
    try:
        if connected and connection.is_connected():
            # setup variables
            table = "DB_" + str(serverID)
            MySql_Insert_Row_Query = "INSERT INTO " + table + " (UserId, UserStr, Currency) VALUES (%(userId)s, %(userstr)s, %(value)s) ON DUPLICATE KEY UPDATE Currency=%(value)s"
            MySql_Insert_Row_values = {'userId': int(user.id), 'userstr': str(user), 'value': data}

            # insert data
            cursor.execute(MySql_Insert_Row_Query, MySql_Insert_Row_values)
            connection.commit()                

            #close connections
            cursor.close()
            connection.close()
            print("MySQL connection has been closed")
            return True
        else:
            print("Failed to connect to database somehow")
            return False
    except:
        print("Failed to insert with {} and {}".format(str(user.id), data))
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
            await interaction.response.send_message("I have stored your data for you!")
        else:
            await interaction.response.send_message("Uh oh! I'm having trouble connecting right now.")
        
    @nextcord.slash_command(name = "retrieve-info", description = "Retrieve some data", guild_ids = [serverId])
    async def retrieve_info (self, interaction : Interaction):        

        serverId = interaction.guild.id
        table = "DB_" + str(serverId)

        # connect to database
        connected = False;
        try:
            # create connection to sql server
            connection = mysql.connector.connect(host=HOST,
                                                database = DATABASE,
                                                user = USER,
                                                password = PASSWORD)
            connected = True;
        except:
            print("Failed to connect to database")
            #return False
            return

        try:
            cursor = connection.cursor()
            
            MySql_Select_Query = "SELECT * FROM " + table + " WHERE UserId LIKE " + str(interaction.user.id)
            cursor.execute(MySql_Select_Query)

            record = cursor.fetchall()
            ReceivedData = []
            for row in record:
                ReceivedData.append({"UserId": row[0], "Currency": str(row[2])})
            
            await interaction.response.send_message("Your data: {}".format(  ReceivedData[0].get("Currency")    ))
        except Exception as e:
            print("Failed to retrieve data: {}".format(e))
            await interaction.response.send_message("Uh oh! I could not retrieve that data from the database")
        
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()






# export cog to bot
def setup(bot: commands.Bot) :
    bot.add_cog(Data(bot))