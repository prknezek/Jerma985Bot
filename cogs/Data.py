import mysql.connector
import nextcord
from nextcord import Interaction
from nextcord.ext import commands

from apikeys import *

# Database login details:
HOST = 'localhost'
DATABASE = 'jerma985bot'
USER = 'root'
PASSWORD = 'root'

# round function - credit to https://medium.com/thefloatingpoint/pythons-round-function-doesn-t-do-what-you-think-71765cfa86a8
def normal_round(num, ndigits=0):
    """
    Rounds a float to the specified number of decimal places.
    num: the value to round
    ndigits: the number of digits to round to
    """
    if ndigits == 0:
        return int(num + 0.5)
    else:
        digit_value = 10 ** ndigits
        return int(num * digit_value + 0.5) / digit_value

# function to store currency into database
# returns boolean: True if successful, False if unsuccessful
# serverID should be id of guild (interaction.guild.id) - used for identifying table
# user should be the user object (interaction.user) - used for ID and username
# data should be a dictionary with key, value pairs to be stored in the database - needs to be a curly bracket {}
#       ex: { "currency": $20, "wins": 2 }
# they will all be stored as strings with length 500
def storeData(serverID, user, data):
    
    # ---------------------------------------------------------------------------- #
    #                              connect to database                             #
    # ---------------------------------------------------------------------------- #
    connected = False
    try:
        # create connection to sql server
        connection = mysql.connector.connect(host=HOST,
                                             database = DATABASE,
                                             user = USER,
                                             password = PASSWORD)
        connected = True
    except:
        print("Failed to connect to database")
        return False
    
    table = "db_" + str(serverID)
    cursor = connection.cursor()
    
    # ---------------------------------------------------------------------------- #
    #                                  setup table                                 #
    # ---------------------------------------------------------------------------- #
    try:

        # ---------------------------- create table query ---------------------------- #
        MYSQL_CREATE_TABLE_QUERY = "CREATE TABLE " + table + " (UserId bigint NOT NULL, UserStr varchar(250) NOT NULL,"
        for col in data.keys():
            MYSQL_CREATE_TABLE_QUERY += str(col) + " varchar(500),"
        MYSQL_CREATE_TABLE_QUERY += "PRIMARY KEY (UserId))"

        # ------------------------------- execute query ------------------------------ #
        result = cursor.execute(MYSQL_CREATE_TABLE_QUERY)
        print("Server (" + str(serverID) + ") Table created successfully")

    # --------------- table exists, so update columns if we need to -------------- #
    except mysql.connector.Error as error:
        print("Failed to create table in MySql: {}".format(error))

        try:
            # fetch current column names from database            
            cols = [i[0] for i in cursor.description]            
            
            # create query
            MYSQL_ADD_COLUMNS_QUERY = "ALTER TABLE " + table + " "
            comma = False
            for requestedCol in data.keys():
                if str(requestedCol) not in cols:
                    if comma:
                        MYSQL_ADD_COLUMNS_QUERY += ", "                    
                    MYSQL_ADD_COLUMNS_QUERY += "ADD COLUMN " + requestedCol + " varchar(500)"
                    comma = True
            print(MYSQL_ADD_COLUMNS_QUERY)      

            # execute query if there are columns that need to be added
            if comma:
                result = cursor.execute(MYSQL_ADD_COLUMNS_QUERY)
                                  
        except Exception as e:
            print("exception: {}".format(str(e)))
            print(MYSQL_ADD_COLUMNS_QUERY)
    
    # ---------------------------------------------------------------------------- #
    #                            insert data into table                            #
    # ---------------------------------------------------------------------------- #
    try:
        if connected and connection.is_connected():
            
            # ---------------------------------------------------------------------------- #
            #                           SQL insert query creation                          #
            # ---------------------------------------------------------------------------- #
            MYSQL_INSERT_ROW_QUERY = "INSERT INTO " + table + " (UserId, UserStr,"

            # -------------------------------- add columns ------------------------------- #
            comma = False
            for col in data.keys():
                if comma:
                    MYSQL_INSERT_ROW_QUERY += ","                    
                MYSQL_INSERT_ROW_QUERY += str(col)
                comma = True
            MYSQL_INSERT_ROW_QUERY += ") VALUES (%(userId)s,%(userstr)s,"
            MySql_Insert_Row_values = {'userId': int(user.id), 'userstr': str(user)}
            
            # -------------------------------- add values -------------------------------- #
            i = 0
            comma = False
            for col in data.keys():
                if comma:
                    MYSQL_INSERT_ROW_QUERY += ","                    
                MYSQL_INSERT_ROW_QUERY += "%("+str(i)+")s"
                MySql_Insert_Row_values[str(i)] = str(data.get(col))
                comma = True
                i += 1
            MYSQL_INSERT_ROW_QUERY += ")"
            
            # ------------------------ add 'on duplicate key' part ----------------------- #
            # this ensures that if data exists, it is just updated
            MYSQL_INSERT_ROW_QUERY += " ON DUPLICATE KEY UPDATE "            
            i = 0
            comma = False
            for col in data.keys():
                if comma:
                    MYSQL_INSERT_ROW_QUERY += ","                    
                MYSQL_INSERT_ROW_QUERY += str(col) + " = " + "%("+str(i)+")s"
                comma = True
                i += 1

            # ---------------------------------------------------------------------------- #
            #                                 execute query                                #
            # ---------------------------------------------------------------------------- #
            cursor.execute(MYSQL_INSERT_ROW_QUERY, MySql_Insert_Row_values)
            connection.commit()                
            print("stored")

            # ---------------------------------------------------------------------------- #
            #                               close connections                              #
            # ---------------------------------------------------------------------------- #
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



# function to retrieve data
# returns a list of strings in the order that data is presented
# serverID should be id of guild (interaction.guild.id) - used for identifying table
# user should be the user object (interaction.user) - used for ID and username
# data should be a tuple or list with strings of column names to be extracted
#       ex: ("money",)
#       ex: ["money"]
#       ex: ["money", "wins"]
def retrieveData(serverID, user, data):

    # table name in database
    table = "DB_" + str(serverID)

    # ---------------------------------------------------------------------------- #
    #                              connect to database                             #
    # ---------------------------------------------------------------------------- #
    connected = False
    try:
        # create connection to sql server
        connection = mysql.connector.connect(host=HOST,
                                            database = DATABASE,
                                            user = USER,
                                            password = PASSWORD)
        connected = True
    except:
        print("Failed to connect to database")
        return None

    # ---------------------------------------------------------------------------- #
    #                                 retrieve data                                #
    # ---------------------------------------------------------------------------- #
    try:
        cursor = connection.cursor()
        
        # ------------------------- SQL select query creation ------------------------ #
        MYSQL_SELECT_QUERY = "SELECT "
        comma = False
        for col in data:
            if comma:
                MYSQL_SELECT_QUERY += ","
            MYSQL_SELECT_QUERY += str(col)
            comma = True
        MYSQL_SELECT_QUERY += " FROM " + table + " WHERE UserId LIKE " + str(user.id)
        print(MYSQL_SELECT_QUERY)

        # ------------------------------- execute query ------------------------------ #
        if comma:
            cursor.execute(MYSQL_SELECT_QUERY)

            # --------------------------- fetch and return data -------------------------- #
            record = cursor.fetchall()
            receivedData = []
            for row in record:
                for data in row:
                    receivedData.append(str(data))

            print("Returning retrieved data")
            return receivedData
        else:
            print("Requested nothing??")
            return None
        
    except Exception as e:
        print("Failed to retrieve data: {}".format(e))
        return None
    
    # ---------------------------------------------------------------------------- #
    #                               close connection                               #
    # ---------------------------------------------------------------------------- #
    finally:
        if connected and connection.is_connected():
            cursor.close()
            connection.close()



class Data(commands.Cog) :
    # ---------------------------------------------------------------------------- #
    #                                initialize cog                                #
    # ---------------------------------------------------------------------------- #
    def __init__(self, bot: commands.Bot) :
        self.bot = bot

    serverId = 1033811091828002817

    @commands.Cog.listener()
    async def on_ready(self):
        print("Data Cog Loaded")


    # ---------------------------------------------------------------------------- #
    #                               set-money command                              #
    # ---------------------------------------------------------------------------- #
    @nextcord.slash_command(name = "set-money", description = "Set money amount for yourself", guild_ids = [serverId])
    async def set_money (self, interaction : Interaction, amount:float):
        amount = normal_round(amount, 2)
        serverID = interaction.guild.id
        success = storeData(serverID, interaction.user, {'MONEY': amount})
        if success:
            await interaction.response.send_message("I have stored your data for you!")
        else:
            await interaction.response.send_message("Uh oh! I'm having trouble connecting right now.")
    
    # ---------------------------------------------------------------------------- #
    #                        retrieve info command (general)                       #
    # ---------------------------------------------------------------------------- #
    @nextcord.slash_command(name = "retrieve-info", description = "Retrieve some data", guild_ids = [serverId])
    async def retrieve_info (self, interaction : Interaction, attribute:str):        
        data = retrieveData(interaction.guild.id, interaction.user, (attribute,))                
        if data != None:
            datastr = ""
            for x in data:
                datastr += str(x)
            await interaction.response.send_message("Your data: {}".format(datastr))
        else:
            await interaction.response.send_message("Uh oh! I could not retrieve that data from the database")

    # ---------------------------------------------------------------------------- #
    #                               retrieve balance                               #
    # ---------------------------------------------------------------------------- #
    @nextcord.slash_command(name = "balance", description = "Retrieve balance", guild_ids = [serverId])
    async def retrieve_bal (self, interaction : Interaction):        
        data = retrieveData(interaction.guild.id, interaction.user, ('money',))                
        if data != None:
            datastr = ""
            for x in data:
                datastr += str(x)
            await interaction.response.send_message("Your data: ${:.2f}".format(float(datastr)))
        else:
            await interaction.response.send_message("Uh oh! I could not retrieve that data from the database")
        


# export cog to bot
def setup(bot: commands.Bot) :
    bot.add_cog(Data(bot))