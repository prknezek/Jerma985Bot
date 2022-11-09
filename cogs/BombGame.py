import nextcord
from nextcord.ext import commands
from nextcord import Interaction
from nextcord import SlashOption
import requests
from random import randint

class Buttons(nextcord.ui.View) :
    def __init__(self) :
        # timeout means the button wont disappear
        super().__init__(timeout = None)
        self.value = None
    
    @nextcord.ui.button(label = "Button", style = nextcord.ButtonStyle.blurple)
    async def button(self, button : nextcord.ui.Button, interaction : Interaction) :
        # ephemeral = True means that only user that send that command can see that message
        await interaction.send("Clicked Button", ephemeral=False)
        self.value = True # allows us to determine if button is clicked
        self.stop()

    @nextcord.ui.button(label = "Test", style = nextcord.ButtonStyle.gray)
    async def test1(self, button : nextcord.ui.Button, interaction : Interaction) :
        # ephemeral = True means that only user that send that command can see that message
        await interaction.send("Clicked Test", ephemeral=False)
        self.value = False # allows us to determine if button is clicked
        self.stop()
    
    @nextcord.ui.button(label = "Test", style = nextcord.ButtonStyle.gray)
    async def test11(self, button : nextcord.ui.Button, interaction : Interaction) :
        # ephemeral = True means that only user that send that command can see that message
        await interaction.send("Clicked Test", ephemeral=False)
        self.value = False # allows us to determine if button is clicked
        self.stop()

class Buttons2(nextcord.ui.View) :
    def __init__(self) :
        # timeout means the button wont disappear
        super().__init__(timeout = None)
        self.value = None
    
    @nextcord.ui.button(label = "Button", style = nextcord.ButtonStyle.blurple)
    async def button(self, button : nextcord.ui.Button, interaction : Interaction) :
        # ephemeral = True means that only user that send that command can see that message
        await interaction.send("Clicked Button", ephemeral=False)
        self.value = True # allows us to determine if button is clicked
        self.stop()

    @nextcord.ui.button(label = "Test", style = nextcord.ButtonStyle.gray)
    async def test1(self, button : nextcord.ui.Button, interaction : Interaction) :
        # ephemeral = True means that only user that send that command can see that message
        await interaction.send("Clicked Test", ephemeral=False)
        self.value = False # allows us to determine if button is clicked
        self.stop()
    
    @nextcord.ui.button(label = "Test", style = nextcord.ButtonStyle.gray)
    async def test11(self, button : nextcord.ui.Button, interaction : Interaction) :
        # ephemeral = True means that only user that send that command can see that message
        await interaction.send("Clicked Test", ephemeral=False)
        self.value = False # allows us to determine if button is clicked
        self.stop()

class BombGame(commands.Cog):
    def __init__(self, bot : commands.Bot) :
        self.bot = bot
    
    serverId = 1033811091828002817

    @nextcord.slash_command(name = "button", description="Button", guild_ids=[serverId])
    async def testing_buttons(self, interaction : Interaction) :
        view = Buttons()
        await interaction.send("You have two options", view=view)
        await interaction.channel.send(view=Buttons2())
        await view.wait() # wait for button to be clicked

        if view.value is None :
            return
        elif view.value :
            print ("You clicked the button")
        else :
            print ("other option")

    @commands.Cog.listener()
    async def on_ready(self) :
        print("Bomb Game Cog Loaded")

def setup(bot: commands.Bot) :
    bot.add_cog(BombGame(bot))