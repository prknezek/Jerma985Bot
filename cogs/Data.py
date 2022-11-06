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
# serverID should be id of guild (interaction.guild.id) - used for identifying table
# user should be the user object (interaction.user) - used for ID and username
# data should be a dictionary with key, value pairs to be stored in the database
# ex: { "currency": $20, "dubs": 2 }
# they will all be stored as strings with length 500
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
    
    table = "db_" + str(serverID)
    cursor = connection.cursor()
    
    # create a table if not already done
    try:    
        # create a table for the data (will error if it already exists)
        MYSQL_CREATE_TABLE_QUERY = "CREATE TABLE " + table + " (UserId bigint NOT NULL, UserStr varchar(250) NOT NULL,"
        for col in data.keys():
            MYSQL_CREATE_TABLE_QUERY += str(col) + " varchar(500),"
        MYSQL_CREATE_TABLE_QUERY += "PRIMARY KEY (UserId))"

        # mySql_Create_Table_Query = """CREATE TABLE DB_""" + str(serverID) + """ (
        #                          UserId bigint NOT NULL,
        #                          UserStr varchar(250) NOT NULL,
        #                          Currency varchar(500) NOT NULL,
        #                          PRIMARY KEY (UserId)) """

        result = cursor.execute(MYSQL_CREATE_TABLE_QUERY)
        print("Server (" + str(serverID) + ") Table created successfully")

    except mysql.connector.Error as error:
        print("Failed to create table in MySql: {}".format(error))
        try:
            
            cursor.execute("SELECT * FROM " + table + " WHERE 1")
            record = cursor.fetchall()

            descriptionTuples = cursor.description
            num_cols = len(descriptionTuples)                        
            cols = [i[0] for i in cursor.description]
            
            
            
            MYSQL_ADD_COLUMNS_QUERY = "ALTER TABLE " + table + " "
            comma = False
            for requestedCol in data.keys():
                if str(requestedCol) not in cols:
                    if comma:
                        MYSQL_ADD_COLUMNS_QUERY += ", "                    
                    MYSQL_ADD_COLUMNS_QUERY += "ADD COLUMN " + requestedCol + " varchar(500)"
                    comma = True
            print(MYSQL_ADD_COLUMNS_QUERY)      
            if comma:
                result = cursor.execute(MYSQL_ADD_COLUMNS_QUERY)
                                  
        except Exception as e:
            print("exception: {}".format(str(e)))
            print(MYSQL_ADD_COLUMNS_QUERY)
    
    # insert data into database
    try:
        if connected and connection.is_connected():
            # setup variables            
            MYSQL_INSERT_ROW_QUERY = "INSERT INTO " + table + " (UserId, UserStr,"
            
            # add columns
            comma = False
            for col in data.keys():
                if comma:
                    MYSQL_INSERT_ROW_QUERY += ","                    
                MYSQL_INSERT_ROW_QUERY += str(col)
                comma = True
            
            MYSQL_INSERT_ROW_QUERY += ") VALUES (%(userId)s,%(userstr)s,"
            MySql_Insert_Row_values = {'userId': int(user.id), 'userstr': str(user)}

            # add values
            i = 0;
            comma = False
            for col in data.keys():
                if comma:
                    MYSQL_INSERT_ROW_QUERY += ","                    
                MYSQL_INSERT_ROW_QUERY += "%("+str(i)+")s"
                MySql_Insert_Row_values[str(i)] = str(data.get(col))
                comma = True
                i += 1
            
            MYSQL_INSERT_ROW_QUERY += ") ON DUPLICATE KEY UPDATE "

            i = 0
            comma = False
            for col in data.keys():
                if comma:
                    MYSQL_INSERT_ROW_QUERY += ","                    
                MYSQL_INSERT_ROW_QUERY += str(col) + " = " + "%("+str(i)+")s"
                comma = True
                i += 1
             


            # insert data
            cursor.execute(MYSQL_INSERT_ROW_QUERY, MySql_Insert_Row_values)
            connection.commit()                

            #close connections
            cursor.close()
            connection.close()
            print("MySQL connection has been closed")
            return True
        else:
            print("Failed to connect to database somehow")
            return False
    except Exception as e:
        print("Failed to insert data: {}".format(str(e)))        
        print(MYSQL_INSERT_ROW_QUERY)
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
        success = storeData(serverID, interaction.user, {'MESSAGE': message, 'MONEY': "$30", 'huh': "bruh"})
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