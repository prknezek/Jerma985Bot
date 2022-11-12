from random import randint

import nextcord
from nextcord import Interaction, SlashOption
from nextcord.ext import commands

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

    @nextcord.slash_command(name = "wiki", description="Link to Jerma wiki", guild_ids=[serverId])
    async def wiki_link(self, interaction : Interaction) :
        await interaction.response.send_message("https://jerma-lore.fandom.com/wiki/Jerma985")

    @nextcord.slash_command(name = "rwikipage", description="Link to a random Jerma wikipage", guild_ids=[serverId])
    async def wiki_link(self, interaction : Interaction) :
        numsites = len(wikisites)
        siteindex = randint(0, numsites-1)
        await interaction.response.send_message(f"{wikisites[siteindex]}")

# export cog to bot
def setup(bot: commands.Bot) :
    bot.add_cog(UI(bot))