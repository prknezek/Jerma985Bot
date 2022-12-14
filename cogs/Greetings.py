import json
import nextcord
import requests
from nextcord import Interaction
from nextcord.ext import commands

import cogs.Data as database
from apikeys import *


class Greetings(commands.Cog) :
    # ----------initialize cog----------
    def __init__(self, bot: commands.Bot) :
        self.bot = bot

    serverId = 1033811091828002817

    @commands.Cog.listener()
    async def on_ready(self):
        print("Greetings Cog Loaded")

    # ------------------------------ first function ------------------------------ #

    @nextcord.slash_command(name="hello", description="says hello", guild_ids=[serverId])
    async def hello(self, interaction : Interaction):
        await interaction.send("Hello")

    # skullface command
    @nextcord.slash_command(name="skullface", description="sends multiple skullface emojis", guild_ids=[serverId])
    async def skullface(self, interaction : Interaction, number: int):
        if number > 285:
            number = 285
            print("reset number")
        skullfaces = ""
        for i in range(int(number)):
            skullfaces = skullfaces + ":skull:"
        await interaction.send(skullfaces)

    # --------------------------- new member join event -------------------------- #
    @commands.Cog.listener()
    async def on_member_join(self, member: nextcord.Member) :

        # importing random joke from joke api
        jokeurl = "https://jokeapi-v2.p.rapidapi.com/joke/Any"

        querystring = {"format":"json","idRange":"0-150","blacklistFlags":"nsfw,racist"}

        headers = {
            "X-RapidAPI-Key": JOKEAPI,
            "X-RapidAPI-Host": "jokeapi-v2.p.rapidapi.com"
        }

        response = requests.request("GET", jokeurl, headers=headers, params=querystring)

        await member.send(f"Welcome {member.mention}! Here's a joke for you.")

        if json.loads(response.text)['type'] == "twopart" :
            await member.send(f"{json.loads(response.text)['setup']}")
            await member.send(f"{json.loads(response.text)['delivery']}")
        else :
            await member.send(f"{json.loads(response.text)['joke']}")

        # give new member some money
        database.storeData(member.guild.id, member, {'money': "30"})
        embed = nextcord.Embed(title="Welcome Gift", color=0x508f4a)
        mr_green_url = "https://static.wikia.nocookie.net/jerma-lore/images/2/25/MrGreen_RosterFace.png/revision/latest/top-crop/width/360/height/360?cb=20210426041715"
        embed.set_author(name= "Mr. Green's Casino", icon_url=mr_green_url)
        embed.add_field(name="Welcome!",value="Here's a gift of $30 from Mr. Green himself!")

        await member.send(embed=embed)

# export cog to bot
def setup(bot: commands.Bot) :
    bot.add_cog(Greetings(bot))