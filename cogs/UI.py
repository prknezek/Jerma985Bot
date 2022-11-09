import nextcord
from nextcord.ext import commands
from nextcord import Interaction
from nextcord import SlashOption
import requests
from random import randint

# load names for birthday messsage
bdaynames = []
f = open("./cogs/resources/birthdaynames.txt")
for name in f.readlines():
    bdaynames.append(name.lower()[:-1])
bdaynames[len(bdaynames)-1] = "zoe"
f.close()

# load wiki pages
wikisites = []
f = open("./cogs/resources/wikisites.txt")
for site in f.readlines():
    wikisites.append(str(site).strip())
f.close()

# test button
# class Buttons(nextcord.ui.View) :
#     def __init__(self) :
#         # timeout means the button wont disappear
#         super().__init__(timeout = None)
#         self.value = None
    
#     @nextcord.ui.button(label = "Button", style = nextcord.ButtonStyle.blurple)
#     async def button(self, button : nextcord.ui.Button, interaction : Interaction) :
#         # ephemeral = True means that only user that send that command can see that message
#         await interaction.send("Clicked Button", ephemeral=False)
#         self.value = True # allows us to determine if button is clicked
#         self.stop()

#     @nextcord.ui.button(label = "Test", style = nextcord.ButtonStyle.gray)
#     async def test1(self, button : nextcord.ui.Button, interaction : Interaction) :
#         # ephemeral = True means that only user that send that command can see that message
#         await interaction.send("Clicked Test", ephemeral=False)
#         self.value = False # allows us to determine if button is clicked
#         self.stop()
    
#     @nextcord.ui.button(label = "Test", style = nextcord.ButtonStyle.gray)
#     async def test11(self, button : nextcord.ui.Button, interaction : Interaction) :
#         # ephemeral = True means that only user that send that command can see that message
#         await interaction.send("Clicked Test", ephemeral=False)
#         self.value = False # allows us to determine if button is clicked
#         self.stop()

# # class to make the dropdown
# class Dropdown(nextcord.ui.Select) :
#     def __init__(self) :
#         select_options = [ nextcord.SelectOption(label="hmm", description="test") ]
#         super().__init__(placeholder="Dropdown Options:", min_values=1, max_values=1, options=select_options)
        
#     async def callback(self, interaction : Interaction) :
#         # user selected options are stored in values
#         if self.values[0] == 'Item 1' :
#             return await interaction.response.send_message("Clicked Item 1")
#         elif self.values[0] == 'Item 2' :
#             return await interaction.send("Clicked Item 2")
#         else :
#             return await interaction.send("Clicked Item 3")

# # class to render the dropdown
# class DropdownView(nextcord.ui.View) :
#     def __init__(self) :
#         super().__init__()
#         self.add_item(Dropdown())
#         self.add_item(Dropdown())

class BdayDropdown(nextcord.ui.Select) :

    def __init__(self, name: str) :
        select_options = [ nextcord.SelectOption(label=name[0].upper()+name[1:]+" Style 1", value=name + "1", description="Birthday Video Style 1"),
                           nextcord.SelectOption(label=name[0].upper()+name[1:]+" Style 2", value=name + "2", description="Birthday Video Style 2") ]
        super().__init__(placeholder="Video Style:", min_values=1, max_values=1, options=select_options)

    async def callback(self, interaction : Interaction) :
        # user selected options are stored in values
        print(self.values[0])

        style = self.values[0][-1:]
        name = self.values[0][:-1]

        return await interaction.send("https://cameoapi.jerma.io/?type=birthday_type0{}&name1={}".format(style, name))

class BdayDropdownView(nextcord.ui.View) :
    def __init__(self, name:str) :
        super().__init__()
        self.add_item(BdayDropdown(name=name))

class UI(commands.Cog) :
    def __init__(self, bot : commands.Bot) :
        self.bot = bot

    serverId = 1033811091828002817

    @commands.Cog.listener()
    async def on_ready(self) :
        print("UI Cog Loaded")

    @nextcord.slash_command(name="birthday-supported-names", description="DM's a list of supported birthday names", guild_ids=[serverId])
    async def birthdayNamesDM(self, interaction : Interaction):
        allnames = ""
        for name in bdaynames:
            allnames += name[0].upper()+name[1:] + "\n"
        embed = nextcord.Embed(title="List of Supported Names for Birthday Message: ", description=allnames)
        await interaction.user.send(embed=embed)
        await interaction.send("Sent! Check your DMs.", ephemeral=True)

    @nextcord.slash_command(name="birthday-message", description="sends a personalized jerma birthday message", guild_ids=[serverId])
    async def birthdayMsg(self, interaction : Interaction, name: str = SlashOption(name="name", description="For list of supported names, type /birthday-supported-names")) :
        name = name.lower()
        if name not in bdaynames:
            await interaction.send("Name unavailable!")
            return
        
        view = BdayDropdownView(name=name)
        # interaction.daname = name
        await interaction.send("Choose a birthday message style for "+name[0].upper()+name[1:], view=view)

    # function name cannot be same name as a button
    # @nextcord.slash_command(name = "button", description="Button", guild_ids=[serverId])
    # async def testing_buttons(self, interaction : Interaction) :
    #     view = Buttons()
    #     await interaction.send("You have two options", view=view)
    #     await interaction.channel.send(view=Buttons2())
    #     await view.wait() # wait for button to be clicked

    #     if view.value is None :
    #         return
    #     elif view.value :
    #         print ("You clicked the button")
    #     else :
    #         print ("other option")
    
    # @nextcord.slash_command(name="dropdown", description="creates a dropdown", guild_ids=[serverId])
    # async def drop(self, interaction : Interaction) :
    #     view = DropdownView()
    #     await interaction.send("Here's a dropdown", view=view)

    @nextcord.slash_command(name = "wiki", description="Link to Jerma wiki", guild_ids=[serverId])
    async def wiki_link(self, interaction : Interaction) :
        await interaction.response.send_message("https://jerma-lore.fandom.com/wiki/Jerma985")

    @nextcord.slash_command(name = "rwikipage", description="Link to a random Jerma wikipage", guild_ids=[serverId])
    async def wiki_link(self, interaction : Interaction) :
        numsites = len(wikisites)
        siteindex = randint(0, numsites-1)
        await interaction.response.send_message(f"{wikisites[siteindex]}")
    
def setup(bot: commands.Bot) :
    bot.add_cog(UI(bot))