import nextcord
from nextcord.ext import commands
from nextcord import Interaction
from nextcord import SlashOption
import requests
from random import randint
import asyncio
import cogs.Data as database

# Global Variables
LOCK = "\U0001f512"
DOLLAR = "\U0001f4b5"
GEM = "\U0001f48e"
BOMB = "\U0001f4a3"

NUM_BOMBS = 3

MULTIPLIER_CONSTANT = 1.25

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
    # typeint - defined in global variables
    def __init__(self, typeint:int, index:int):
        #timeout?
        self.typeint = typeint
        if typeint == UNPRESSED_MONEY or typeint == UNPRESSED_BOMB:
            super().__init__(style=nextcord.ButtonStyle.blurple, emoji=LOCK)
        elif typeint == PRESSED_MONEY:
            super().__init__(style=nextcord.ButtonStyle.green, emoji=DOLLAR)
        elif typeint == PRESSED_BOMB:
            super().__init__(style=nextcord.ButtonStyle.red, emoji=BOMB)
        elif typeint == 4: # show all in grey
            super().__init__(style=nextcord.ButtonStyle.grey, emoji=DOLLAR)
        elif typeint == 5: # show all in grey
            super().__init__(style=nextcord.ButtonStyle.grey, emoji=BOMB)

        self.index = index

    async def callback(self, interaction:Interaction):
        if self.typeint == UNPRESSED_MONEY or self.typeint == UNPRESSED_BOMB:
            print("clicked {}, going into row".format(str(self.index)))
            if self.typeint == UNPRESSED_BOMB:
                self.view.gameover = True
            self.view.customRefresh(index=self.index)


# the view class (1 view per row)
class Row(nextcord.ui.View) :
    def __init__(self, rowmatrix):
        # timeout means the button wont disappear
        print("init row {}".format(str(rowmatrix)))
        super().__init__(timeout = None)

        self.clicked = None             # might not need
        self.gameover = False
        self.rowmatrix = rowmatrix

        i = 0
        for col in rowmatrix:
            tile = Tile(typeint=col, index=i)
            self.add_item(tile)
            i += 1
    
    def customRefresh(self, index:int):
        print("received {}, setting clicked to true".format(index))

        self.rowmatrix[index] += 2

        self.clicked = True              # might not need

        stopAllViews()

class Payout(nextcord.ui.Button):
    def __init__(self):
        super().__init__(label="Payout",style=nextcord.ButtonStyle.green)
        
    
    async def callback(self, interaction: Interaction):
        self.view.gameover = True
        stopAllViews()
        print("payout")

class actionBar(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout = None)
        self.add_item(Payout())
        self.gameover = False


class BombGame(commands.Cog):
    def __init__(self, bot : commands.Bot) :
        self.bot = bot
    
    serverId = 1033811091828002817

    @nextcord.slash_command(name = "bombtiles", description="A gambling game", guild_ids=[serverId])
    async def bomb_tiles(self, interaction : Interaction, starting_bet:float = SlashOption(name="bet",description="Input an amount to bet")) :
        
        # check if starting_bet is valid
        starting_bet = database.normal_round(starting_bet, 2)        
        if starting_bet <= 0.00:
            return await interaction.send("What, you think I'm an idiot?! - Mr. Green", ephemeral=True)

        # check balance and take money away from user
        try:
            user_balance_raw = database.retrieveData(interaction.guild.id, interaction.user, ['MONEY'])[0]
        except:
            return await interaction.send("Uh oh! I couldn't connect to the database.")
        if user_balance_raw[0] == '$':
            user_balance = float(user_balance_raw[1:])
        else:
            user_balance = float(user_balance_raw)
        if user_balance < starting_bet:
            return await interaction.send("You're too broke to play! - Mr. Green", ephemeral=True)
        user_balance -= starting_bet
        database.storeData(interaction.guild.id, interaction.user, {'MONEY': str(user_balance)})

        # send instructions
        embed = nextcord.Embed(title="Bomb Tiles", color=0x508f4a)
        mr_green_url = "https://static.wikia.nocookie.net/jerma-lore/images/2/25/MrGreen_RosterFace.png/revision/latest/top-crop/width/360/height/360?cb=20210426041715"
        embed.set_author(name= "Mr. Green's Casino", icon_url=mr_green_url)
        embed.add_field(name="Click on the tiles to increase your payout, but watch out for the bombs!\n------------------------------------------------------------------------------------", 
                        value="**${:.2f}** has been **withdrawn** from {}'s account!".format(starting_bet, str(interaction.user)))
        await interaction.send(embed=embed)

        # send bet info
        bet = starting_bet
        multiplier = 1
        infoMessage = await interaction.channel.send("Loading...")

        # keep track of stuff
        # defined in global variables
        matrix=[[UNPRESSED_MONEY,UNPRESSED_MONEY,UNPRESSED_MONEY],
                [UNPRESSED_MONEY,UNPRESSED_MONEY,UNPRESSED_MONEY],
                [UNPRESSED_MONEY,UNPRESSED_MONEY,UNPRESSED_MONEY]]
        views.clear()
        viewMessages = []
        game_over = False
        

        # randomize bomb location
        bombLocations = []
        for i in range(NUM_BOMBS):
            bombx = randint(0,2)
            bomby = randint(0,2)
            bombLoc = (bombx, bomby)
            while bombLoc in bombLocations:
                bombx = randint(0,2)
                bomby = randint(0,2)
                bombLoc = (bombx, bomby)
            bombLocations.append(bombLoc)
            matrix[bombx][bomby] = UNPRESSED_BOMB

        # create and send views
        i = 0
        for row in matrix:
            view = Row(matrix[i])
            views.append(view)
            viewMessages.append(await interaction.channel.send(view=view))            
            i += 1
        
        # send action bar with payout
        bar = actionBar()
        await interaction.channel.send(view=bar)
        
        # now re-send info message
        payout = bet*multiplier
        await infoMessage.edit("**Bet:** ${:.2f}  **Multiplier:** {:.2f}x  **Payout:** ${:.2f}".format(bet, multiplier, payout))

        count = 0
        while (count < (len(matrix)*len(matrix[0]))-NUM_BOMBS):
            # wait till interaction
            print("waiting...")
            await views[0].wait()
            
            # stop all views and get matrix values again
            i = 0
            for view in views:
                matrix[i] = view.rowmatrix
                if view.gameover:
                    game_over = True
                view.stop()
                print("new matrix: {}".format(str(matrix[i])))            
                i += 1

            #update variables
            if not game_over and not bar.gameover:
                multiplier = database.normal_round(multiplier*MULTIPLIER_CONSTANT, 2)
                payout = database.normal_round(bet*multiplier, 2)
            elif game_over:
                payout = 0

            # RNG'ING...
            if bar.gameover:
                await infoMessage.edit(content="collecting your funds...")
            else:
                await infoMessage.edit(content="rigging your game...")

            # show all tiles in matrix if game over
            if game_over or bar.gameover:
                for x in range(len(matrix)):
                    for y in range(len(matrix[0])):
                        if matrix[x][y] == UNPRESSED_BOMB or matrix[x][y] == UNPRESSED_MONEY:
                            matrix[x][y] += 4


            #for x in viewMessages:
                #await x.edit(content="...", view=None)
            print("sleeping...")
            await asyncio.sleep(2)
            print("done sleeping")

            # update views and message
            i = 0
            for row in matrix:
                newview = Row(matrix[i])
                views[i] = newview
                print("  editing...")
                await viewMessages[i].edit(view=newview)
                print("  edited")
                i += 1

            #update information message 
            await infoMessage.edit(content="**Bet:** ${:.2f}  **Multiplier:** {:.2f}x  **Payout:** ${:.2f}".format(bet, multiplier, bet*multiplier))

            # check if gameover
            if game_over or bar.gameover:
                break
            
            count += 1
        
        # TODO - give money with database
        user_balance += payout
        database.storeData(interaction.guild.id, interaction.user, {'MONEY': str(user_balance)})

        stopAllViews()
        embed = nextcord.Embed(title="Payment", color=0x508f4a, description="**${:.2f}** has been **deposited** to {}'s account!\nTotal Balance: **${:.2f}**".format(payout, str(interaction.user), user_balance))
        embed.set_author(name= "Mr. Green's Casino", icon_url=mr_green_url)
        return await interaction.send(embed=embed)
        

    @commands.Cog.listener()
    async def on_ready(self) :
        print("Bomb Game Cog Loaded")

def setup(bot: commands.Bot) :
    bot.add_cog(BombGame(bot))