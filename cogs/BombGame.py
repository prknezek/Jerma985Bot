import nextcord
from nextcord.ext import commands
from nextcord import Interaction
from nextcord import SlashOption
import requests
from random import randint
import asyncio

# Global Variables
LOCK = "\U0001f512"
DOLLAR = "\U0001f4b5"
GEM = "\U0001f48e"
BOMB = "\U0001f4a3"

MULTIPLIER_CONSTANT = 1.5

UNPRESSED_MONEY = 0
UNPRESSED_BOMB = 1
# add 2 when pressed
PRESSED_MONEY = 2
PRESSED_BOMB = 3

# functionality to stop all views on any button on grid click and maintain flow of program
views = []
def stopAllViews():
    for tempview in views:
        tempview.stop()

# the button class
class Tile(nextcord.ui.Button):
    # type - defined in global variables
    def __init__(self, type:int, index:int):
        #timeout?
        if type == UNPRESSED_MONEY or type == UNPRESSED_BOMB:
            super().__init__(style=nextcord.ButtonStyle.blurple, emoji=LOCK)
        elif type == PRESSED_MONEY:
            super().__init__(style=nextcord.ButtonStyle.green, emoji=DOLLAR)
        else: # type == PRESSED_BOMB
            super().__init__(style=nextcord.ButtonStyle.red, emoji=BOMB)

        self.index = index

    async def callback(self, interaction:Interaction):
        print("clicked {}, going into row".format(str(self.index)))
        self.view.customRefresh(index=self.index)


# the view class (1 view per row)
class Row(nextcord.ui.View) :
    def __init__(self, rowmatrix):
        # timeout means the button wont disappear
        print("init row {}".format(str(rowmatrix)))
        super().__init__(timeout = None)

        self.clicked = None             # might not need
        self.rowmatrix = rowmatrix

        i = 0
        for col in rowmatrix:
            tile = Tile(type=col, index=i)
            self.add_item(tile)
            i += 1
    
    def customRefresh(self, index:int):
        print("received {}, setting clicked to true".format(index))

        self.rowmatrix[index] += 2

        self.clicked = True              # might not need

        stopAllViews()

class BombGame(commands.Cog):
    def __init__(self, bot : commands.Bot) :
        self.bot = bot
    
    serverId = 1033811091828002817

    @nextcord.slash_command(name = "button", description="Button", guild_ids=[serverId])
    async def testing_buttons(self, interaction : Interaction) :
        # send instructions
        await interaction.send("Click on the tiles to increase your payout, and watch out for the bombs!")
        await interaction.channel.send("---------------------------------------------")

        # send bet info
        bet = 20.0
        multiplier = 0.5
        infoMessage = await interaction.channel.send("**Bet:** {}  **Multiplier:** {}x  **Payout:** {}".format(str(bet), str(multiplier), str(bet*multiplier)))

        # keep track of stuff
        # nums - defined in global variables
        matrix=[[1,0,0],
                [0,0,0],
                [0,0,0]]
        # views = [] - moved to global variable
        viewMessages = []

        # create views
        i = 0
        for row in matrix:
            view = Row(matrix[i])
            views.append(view)
            viewMessages.append(await interaction.channel.send(view=view))            
            i += 1
        
        # wait till interaction
        tempcount = 0
        while (tempcount < 8):
            print("waiting...")
            await views[0].wait()
            # breakLoop = False
            # while (breakLoop == False):
            #     for view in views:
            #         if view.clicked == True:
            #             print("breaking...")
            #             breakLoop = True
            #             break
            #         else:
            #             print("bruh")
            
            # stop all views and get matrix values again
            i = 0
            for view in views:
                matrix[i] = view.rowmatrix
                view.stop()
                print("new matrix: {}".format(str(matrix[i])))            
                i += 1

            #update variables
            multiplier *= MULTIPLIER_CONSTANT
            payout = bet*multiplier

            # RNG'ING...
            await infoMessage.edit(content="rigging your game...")
            #for x in viewMessages:
                #await x.edit(content="...", view=None)
            await asyncio.sleep(1)

            # update views and message
            i = 0
            for row in matrix:
                newview = Row(matrix[i])
                views[i] = newview
                await viewMessages[i].edit(view=newview)
                i += 1

            #update information message 
            await infoMessage.edit(content="**Bet:** {}  **Multiplier:** {}  **Payout:** {}".format(str(bet), str(multiplier), str(bet*multiplier)))
            
            tempcount += 1
        

    @commands.Cog.listener()
    async def on_ready(self) :
        print("Bomb Game Cog Loaded")

def setup(bot: commands.Bot) :
    bot.add_cog(BombGame(bot))