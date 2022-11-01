import nextcord
from nextcord.ext import commands
from apikeys import *
import requests
import json

class Greetings(commands.Cog) :
    def __init__(self, bot: commands.Bot) :
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Greetings Cog Loaded")

    @commands.command()
    # name of function is what the user will type to call this command
    async def hello(self, ctx):
        await ctx.send("Hello")

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

    @commands.Cog.listener()
    # when user reacts, function is called
    async def on_reaction_add(self, reaction, user) :
        channel = reaction.message.channel
        await channel.send(user.name + " added: " + reaction.emoji)

    @commands.Cog.listener()
    # when user unreacts, function is called
    async def on_reaction_remove(self, reaction, user) :
        channel = reaction.message.channel
        await channel.send(user.name + " removed: " + reaction.emoji)

    @commands.Cog.listener()
    async def on_message(self, message) :
        # if message was sent by the bot
        if message.author == self.bot.user :
            return
        if "happy" in message.content :
            emoji = '\N{THUMBS UP SIGN}'
            await message.add_reaction(emoji)

# export cog to bot
async def setup(bot: commands.Bot) :
    bot.add_cog(Greetings(bot))