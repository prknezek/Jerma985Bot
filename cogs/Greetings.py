import nextcord
from nextcord.ext import commands
from nextcord import Interaction
from apikeys import *
import requests
import json

class Greetings(commands.Cog) :
    # ----------initialize cog----------
    def __init__(self, bot: commands.Bot) :
        self.bot = bot

    serverId = 1033811091828002817

    @commands.Cog.listener()
    async def on_ready(self):
        print("Greetings Cog Loaded")
    #   ----------done----------


    # name of function is what the user will type to call this command
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

    # new member join event
    @commands.Cog.listener()
    async def on_member_join(self, member: nextcord.Member) :
        # importing random joke from joke api
        jokeurl = "https://jokeapi-v2.p.rapidapi.com/joke/Any"

        querystring = {"format":"json","blacklistFlags":"nsfw,racist"}

        headers = {
            "X-RapidAPI-Key": JOKEAPI,
            "X-RapidAPI-Host": "jokeapi-v2.p.rapidapi.com"
        }

        response = requests.request("GET", jokeurl, headers=headers, params=querystring)

        await member.send(f"Welcome {member.mention}! Here's a joke for you.")
        await member.send(f"{json.loads(response.text)['setup']}") # prints setup into chat
        # response.text is in json so we are filtering the setup attribute
        # out of the response and printing it in nextcord
        await member.send(f"{json.loads(response.text)['delivery']}")

    # when user reacts
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user) :
        channel = reaction.message.channel
        await channel.send(user.name + " added: " + reaction.emoji)

    # when user unreacts
    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user) :
        channel = reaction.message.channel
        await channel.send(user.name + " removed: " + reaction.emoji)

    # when a message is sent
    @commands.Cog.listener()
    async def on_message(self, message) :
        # if message was sent by the bot
        if message.author == self.bot.user :
            return
        if "happy" in message.content :
            emoji = '\N{THUMBS UP SIGN}'
            await message.add_reaction(emoji)

        # WE DO A LITTLE TROLLING
        # if message.author.id == 243898181585207296:                        
        #     await message.channel.send("THE GREAT PAYTON HAS SENT A MESSAGE");
        if "is yeat the best rapper" in message.content :
            await message.channel.send("yes")
        elif "jerma" in message.content and "twizzy" in message.content:
            await message.channel.send("this jerma bot is a certified twizzy");
        elif "fr" in message.content :
            await message.channel.send("no cap")
        elif "no cap" in message.content :
            await message.channel.send("on god");        
        elif "ong" in message.content or "on god" in message.content:
            await message.channel.send("no kizzy")

# export cog to bot
def setup(bot: commands.Bot) :
    bot.add_cog(Greetings(bot))