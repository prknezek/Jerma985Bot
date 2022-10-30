from http import client
from unicodedata import name
from click import pass_context
from numpy import broadcast
import requests
import json
import os
import discord
from discord.ext import tasks, commands
from discord import FFmpegPCMAudio
from discord import Member
from discord.ext.commands import has_permissions, MissingPermissions
from twitchAPI.twitch import Twitch
from discord.utils import get

from apikeys import * # imports variables from local apikeys.py

intents = discord.Intents.all() # make sure commands work
# dictionary to store queued songs
queues = {}

# authentication w/ Twitch API
client_id = TWITCH_CLIENT_ID
client_secret = TWITCH_CLIENT_SECRET_ID
twitch = Twitch(client_id, client_secret)
twitch.authenticate_app([])
TWITCH_STREAM_API_ENDPOINTS_V5 = "https://api.twitch.tv/kraken/streams/{}"
API_HEADERS = {
    'Client-ID' : client_id,
    'Accept' : 'application/vnd.twitchtv.v5+json'
}

# returns true if streamer is online and false if not online
def check_user(user) :
    try:
        userid = twitch.get_users(logins=[user])['data'][0]['id']
        url = TWITCH_STREAM_API_ENDPOINTS_V5.format(userid)
        try :
            req = requests.Session().get(url, headers=API_HEADERS)
            jsondata = req.json()
            if 'stream' in jsondata :
                if jsondata['stream'] is not None :
                    return True
                else :
                    return False
        except Exception as e :
            print("Error checking user: ", e)
            return False
    except IndexError :
        return False

def check_queue(ctx, id) :
    # if there is something in the queue
    if queues[id] != [] :
        voice = ctx.guild.voice_client # create our voice
        source = queues[id].pop(0) # set the source to what is in the queues array
        player = voice.play(source) # play the source

# initialize our bot with command prefix '!'
COMMAND_PREFIX = '!'
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

@bot.event
# when the bot is ready to start receiveing commands it will execute this function
async def on_ready():
    # live streaming detection
    @tasks.loop(minutes=1)
    async def live_notifs_loop() :
        # grabbing info from server
        guild = bot.get_guild(1033811091828002817)
        status = check_user("jerma985")
        channel = bot.get_channel(1036160854460215337)

        # getting twitch info
        broadcaster_info = twitch.get_users(user_ids=None, logins="jerma985")["data"][0]
        broadcaster_id = broadcaster_info['id']
        channel_info = twitch.get_channel_information(broadcaster_id=broadcaster_id)["data"][0]
        stream_name = channel_info["title"]

        print("checking status")
        # checks every minute to see if jerma goes live
        if status :
            # check to see if notification for stream was already sent out to server
            messages = [message async for message in channel.history(limit=50)]
            # if no messages in channel then send live message
            if len(messages) == 0 :
                await channel.send(
                    f":red_circle: **LIVE**\nJerma985 is live on Twitch!"
                    f"\nhttps://www.twitch.tv/jerma985"
                    f"\n@everyone"
                )
            else : # if messages in channel, detect whether or not to delete them
                async for message in channel.history(limit=50) :
                    # if message was sent out then break
                    if "Jerma985 is live on Twitch!" in message.content :
                        break
                    # sends live message if it wasn't sent out yet
                    else :
                        await channel.send(
                            f":red_circle: **LIVE**\nJerma985 is live on Twitch!"
                            f"\nhttps://www.twitch.tv/jerma985"
                            f"@everyone"
                        )
        else :# if they aren't live:
            print("not live")
            async for message in channel.history(limit=200) :
                if "Jerma985 is live on Twitch!" in message.content :
                    await message.delete()

        # if jerma is live change status
        if status :
            await bot.change_presence(status=discord.Status.online, 
            activity=discord.Streaming(name=stream_name, url="https://www.twitch.tv/jerma985"))
        else :
            await bot.change_presence(status=discord.Status.online, 
            activity=discord.CustomActivity(name="test", emoji=":red_circle:"))
    
    # starts the loop to scan for streaming activity
    live_notifs_loop.start()
    # print statement for when bot is ready
    print("Jerma is ready for battle")
    print("-------------------------")

@bot.command()
# name of function is what the user will type to call this command
async def hello(ctx):
    await ctx.send("Hello")

# new member join
@bot.event
async def on_member_join(member) :
    # importing random joke from joke api
    jokeurl = "https://jokeapi-v2.p.rapidapi.com/joke/Any"

    querystring = {"format":"json","blacklistFlags":"nsfw,racist"}

    headers = {
        "X-RapidAPI-Key": JOKEAPI,
        "X-RapidAPI-Host": "jokeapi-v2.p.rapidapi.com"
    }

    response = requests.request("GET", jokeurl, headers=headers, params=querystring)

    channel = bot.get_channel(1033811139034886254) # channel id for bot-commands
    await channel.send("Welcome " + member.name + "!")
    await channel.send(json.loads(response.text)['setup']) # prints setup into chat
    # response.text is in json so we are filtering the setup attribute
    # out of the response and printing it in discord
    await channel.send(json.loads(response.text)['delivery'])

@bot.event
async def on_member_remove(member) :
    channel = bot.get_channel(1033811139034886254)
    await channel.send("Goodbye")

# join and leave commands
# command to allow bot to join a voice channel
@bot.command(pass_context = True)
async def join(ctx) :
    if (ctx.author.voice) : # if user running command is in a voice channel
        channel = ctx.message.author.voice.channel # finds the channel they're in
        voice = await channel.connect() # connects to the channel
        #source = FFmpegPCMAudio('KICK_BACK.wav') # name of audio file
        #player = voice.play(source)
    else :
        await ctx.send("You must be in a voice channel to run this command")

# command to allow bot to leave a voice channel
@bot.command(pass_context = True) 
async def leave(ctx) :
    if (ctx.voice_client) : # if bot is in a voice channel
        await ctx.guild.voice_client.disconnect() # it will disconnect
        await ctx.send("Left the voice channel")
    else :
        await ctx.send("I am not in a voice channel")

# audio commands
@bot.command(pass_context = True) 
async def pause(ctx) :
    # calling discord utils package. voice client is what song its currently playing
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_playing() :
        voice.pause()
    else :
        await ctx.send("No audio currently playing in voice channel")

@bot.command(pass_context = True) 
async def resume(ctx) :
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_paused() :
        voice.resume()
    else :
        await ctx.send("Audio is not paused")

@bot.command(pass_context = True) 
async def stop(ctx) :
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    voice.stop()

# bot plays custom file
@bot.command(pass_context = True) 
async def play(ctx, arg) :
    voice = ctx.guild.voice_client
    song = arg + '.wav'
    source = FFmpegPCMAudio(song)
    player = voice.play(source,
    # after play command is run, check queue
    after = lambda x = None: check_queue(ctx, ctx.message.guild.id))

@bot.command(pass_context = True) 
async def queue(ctx, arg) :
    voice = ctx.guild.voice_client
    song = arg + '.wav'
    source = FFmpegPCMAudio(song)

    guild_id = ctx.message.guild.id
    if guild_id in queues :
        queues[guild_id].append(source)
    else :
        queues[guild_id] = [source]
    
    await ctx.send("Added to queue")
"""
@bot.event
async def on_message(message):
    banned_words = ["hi", "hello"]
    # can replace "hi" with a list of banned words and detect if message in that list
    for word in banned_words :
        if message.content == word :
            await message.delete()
            await message.channel.send("Don't say that again")     
""" 

@bot.command()
@has_permissions(kick_members=True) # checks if user running bot command has permission to kick members
# member is user to be kicked, reason is reason why they were kicked
async def kick(ctx, member: discord.Member, *, reason=None) :
    await member.kick(reason=reason)
    await ctx.send(f'User {member} has been kicked')
    
@kick.error # if user doesn't have permission to kick members
async def kick_error(ctx, error) :
    if isinstance(error, commands.MissingPermissions) :
        await ctx.send("You dont have permission to kick")

@bot.command()
@has_permissions(ban_members=True) # checks if user running bot command has permission to ban members
# member is user to be kicked, reason is reason why they were banned
async def ban(ctx, member: discord.Member, *, reason=None) :
    await member.ban(reason=reason)
    await ctx.send(f'User {member} has been banned')

@kick.error # if user doesn't have permission to ban members
async def ban_error(ctx, error) :
    if isinstance(error, commands.MissingPermissions) :
        await ctx.send("You dont have permission to ban")

@bot.command()
async def embed(ctx) : # *** CAN CHANGE TO JERMA WIKI LINK 
    embed = discord.Embed(title="Test", url="https://google.com", 
    description="Takes you to google", color=0x4dff4d)

    # putting name of member and member avatar in embed
    embed.set_author(name=ctx.author.display_name, url="https://github.com/prknezek/Jerma985Bot", 
    icon_url=ctx.author.display_avatar)

    #thumbnail
    embed.set_thumbnail(url="https://static.wikia.nocookie.net/jerma-lore/images/9/91/Evil_Jerma.png")
    
    embed.add_field(name="Field 1", value="desc for field 1", inline=True)
    embed.add_field(name="Field 2", value="desc for field 2", inline=True)
    
    embed.set_footer(text="Embed footer")
    await ctx.send(embed=embed)

# run the bot after initializing all commands
bot.run(BOTTOKEN)
