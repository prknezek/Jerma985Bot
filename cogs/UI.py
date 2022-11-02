import nextcord
from nextcord.ext import commands
from nextcord import Interaction

# test button
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
    async def test(self, button : nextcord.ui.Button, interaction : Interaction) :
        # ephemeral = True means that only user that send that command can see that message
        await interaction.send("Clicked Test", ephemeral=False)
        self.value = False # allows us to determine if button is clicked
        self.stop()

# class to make the dropdown
class Dropdown(nextcord.ui.Select) :
    def __init__(self) :
        select_options = [
            nextcord.SelectOption(label="Item 1", description="Item 1 in dropdown"),
            nextcord.SelectOption(label="Item 2", description="Item 2 in dropdown"),
            nextcord.SelectOption(label="Item 3", description="Item 3 in dropdown")
        ]
        super().__init__(placeholder="Dropdown Options:", min_values=1, max_values=1, options=select_options)
        
    async def callback(self, interaction : Interaction) :
        # user selected options are stored in values
        if self.values[0] == 'Item 1' :
            return await interaction.response.send_message("Clicked Item 1")
        elif self.values[0] == 'Item 2' :
            return await interaction.send("Clicked Item 2")
        else :
            return await interaction.send("Clicked Item 3")

# class to render the dropdown
class DropdownView(nextcord.ui.View) :
    def __init__(self) :
        super().__init__()
        self.add_item(Dropdown())

class UI(commands.Cog) :
    def __init__(self, bot : commands.Bot) :
        self.bot = bot

    serverId = 1033811091828002817

    @commands.Cog.listener()
    async def on_ready(self) :
        print("UI Cog Loaded")

    # function name cannot be same name as a button
    @nextcord.slash_command(name = "button", description="Button", guild_ids=[serverId])
    async def testing_buttons(self, interaction : Interaction) :
        view = Buttons()
        await interaction.send("You have two options", view=view)
        await view.wait() # wait for button to be clicked

        if view.value is None :
            return
        elif view.value :
            print ("You clicked the button")
        else :
            print ("idk")
    
    @nextcord.slash_command(name="dropdown", description="creates a dropdown", guild_ids=[serverId])
    async def drop(self, interaction : Interaction) :
        view = DropdownView()
        await interaction.send("Here's a dropdown", view=view)
    
def setup(bot) :
    bot.add_cog(UI(bot))