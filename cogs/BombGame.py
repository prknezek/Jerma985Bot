import nextcord
from nextcord.ext import commands
from nextcord import Interaction
from nextcord import SlashOption
import requests
from random import randint

# Global Variables
LOCK = "\U0001f512"
DOLLAR = "\U0001f4b5"
GEM = "\U0001f48e"
BOMB = "\U0001f4a3"

class Buttons(nextcord.ui.View) :
    def __init__(self) :
        # timeout means the button wont disappear
        super().__init__(timeout = None)
        self.value = [[0,0,0], 0]
    
    @nextcord.ui.button(emoji = LOCK)
    async def button(self, button : nextcord.ui.Button, interaction : Interaction) :
        # ephemeral = True means that only user that send that command can see that message
        # await interaction.send("Clicked Button", ephemeral=False)
        self.value[0][0] = 1 # allows us to determine if button is clicked
        self.value[1] += 1
        button.style = nextcord.ButtonStyle.green
        button.emoji = BOMB
        print("changed emoji")
        #self.stop()

    @nextcord.ui.button(emoji = DOLLAR, style = nextcord.ButtonStyle.blurple)
    async def test1(self, button : nextcord.ui.Button, interaction : Interaction) :
        # await interaction.send("Clicked Test", ephemeral=False)
        self.value[0][1] = 1 # allows us to determine if button is clicked
        self.value[1] += 1
        #self.stop()
    
    @nextcord.ui.button(label = BOMB, style = nextcord.ButtonStyle.blurple)
    async def test11(self, button : nextcord.ui.Button, interaction : Interaction) :
        # await interaction.send("Clicked Test", ephemeral=False)
        self.value[0][2] = 1 # allows us to determine if button is clicked
        self.value[1] += 1
        print(self.value)
        #self.stop()

class BombGame(commands.Cog):
    def __init__(self, bot : commands.Bot) :
        self.bot = bot
    
    serverId = 1033811091828002817

    @nextcord.slash_command(name = "button", description="Button", guild_ids=[serverId])
    async def testing_buttons(self, interaction : Interaction) :
        view = Buttons()
        await interaction.send("You have two options", view=view)
        await interaction.channel.send(view=Buttons())
        await view.wait() # wait for button to be clicked

        if view.value is None :
            return
        elif view.value == "test":
            print ("WHAT THE")
        else :
            print ("other option")

    @commands.Cog.listener()
    async def on_ready(self) :
        print("Bomb Game Cog Loaded")

def setup(bot: commands.Bot) :
    bot.add_cog(BombGame(bot))