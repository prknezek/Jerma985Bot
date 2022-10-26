from click import pass_context
import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
import requests
import json

from apikeys import * # imports variables from local apikeys.py

intents = discord.Intents.all() # make sure commands work

# initialize our bot with command prefix '!'
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
# when the bot is ready to start receiveing commands it will execute this function
async def on_ready():
    print("Jerma is ready for battle")
    print("-------------------------")

@bot.command()
# name of function is what the user will type to call this command
async def hello(ctx):
    await ctx.send("Hello")

@bot.event
async def on_member_join(member) :
    # importing random joke from joke api
    jokeurl = "https://jokeapi-v2.p.rapidapi.com/joke/Any"

    querystring = {"format":"json","contains":"C%23","idRange":"0-150","blacklistFlags":"nsfw,racist"}

    headers = {
        "X-RapidAPI-Key": JOKEAPI,
        "X-RapidAPI-Host": "jokeapi-v2.p.rapidapi.com"
    }

    response = requests.request("GET", jokeurl, headers=headers, params=querystring)

    channel = bot.get_channel(1033811139034886254) # channel id for bot-commands
    await channel.send("Welcome")
    await channel.send(json.loads(response.text)['setup']) # prints setup into chat
    # response.text is in json so we are filtering the setup attribute
    # out of the response and printing it in discord
    await channel.send(json.loads(response.text)['delivery'])

@bot.event
async def on_member_remove(member) :
    channel = bot.get_channel(1033811139034886254)
    await channel.send("Goodbye")

# command to allow bot to join a voice channel
@bot.command(pass_context = True)
async def join(ctx) :
    if (ctx.author.voice) : # if user running command is in a voice channel
        channel = ctx.message.author.voice.channel # finds the channel they're in
        voice = await channel.connect() # connects to the channel
        source = FFmpegPCMAudio('KICK_BACK.wav') # name of audio file
        player = voice.play(source)
    else :
        await ctx.send("You must be in a voice channel to run this command")

# command to allow bot to leave a voice channel
@bot.command(pass_context = True) 
async def leave(ctx) :
    if (ctx.voice_client) : # if bot is in a voice channel
        await ctx.guild.voice_client.disconnect() # it will disconnect
        await ctx.send("I left the voice channel")
    else :
        await ctx.send("I am not in a voice channel")


# run the bot after initializing all commands
bot.run(BOTTOKEN)
