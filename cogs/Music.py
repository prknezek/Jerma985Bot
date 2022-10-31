import discord
from discord.ext import commands
from discord import FFmpegPCMAudio

# dictionary to store queued songs
queues = {}

# function checks the current music queue
def check_queue(ctx, id) :
    # if there is something in the queue
    if queues[id] != [] :
        voice = ctx.guild.voice_client # create our voice
        source = queues[id].pop(0) # set the source to what is in the queues array
        player = voice.play(source) # play the source

class Music(commands.Cog) :
    def __init__(self, bot: commands.Bot) :
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Music Cog Loaded")

    @commands.command(pass_context = True)
    async def join(self, ctx) :
        if (ctx.author.voice) : # if user running command is in a voice channel
            channel = ctx.message.author.voice.channel # finds the channel they're in
            voice = await channel.connect() # connects to the channel
        else :
            await ctx.send("You must be in a voice channel to run this command")

    # command to allow bot to leave a voice channel
    @commands.command(pass_context = True) 
    async def leave(self, ctx) :
        if (ctx.voice_client) : # if bot is in a voice channel
            await ctx.guild.voice_client.disconnect() # it will disconnect
            await ctx.send("Left the voice channel")
        else :
            await ctx.send("I am not in a voice channel")

    # audio commands
    @commands.command(pass_context = True) 
    async def pause(self, ctx) :
        # calling discord utils package. voice client is what song its currently playing
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice.is_playing() :
            voice.pause()
        else :
            await ctx.send("No audio currently playing in voice channel")

    @commands.command(pass_context = True) 
    async def resume(self, ctx) :
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice.is_paused() :
            voice.resume()
        else :
            await ctx.send("Audio is not paused")

    @commands.command(pass_context = True) 
    async def stop(self, ctx) :
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        voice.stop()

    # bot plays custom file
    @commands.command(pass_context = True) 
    async def play(self, ctx, arg) :
        voice = ctx.guild.voice_client
        song = arg + '.wav'
        source = FFmpegPCMAudio(f"cogs/audio/{song}")
        player = voice.play(source,
        # after play command is run, check queue
        after = lambda x = None: check_queue(ctx, ctx.message.guild.id))

    @commands.command(pass_context = True) 
    async def queue(self, ctx, arg) :
        voice = ctx.guild.voice_client
        song = arg + '.wav'
        source = FFmpegPCMAudio(f"cogs/audio/{song}")

        guild_id = ctx.message.guild.id
        if guild_id in queues :
            queues[guild_id].append(source)
        else :
            queues[guild_id] = [source]
        await ctx.send("Added to queue")

async def setup(bot: commands.Bot) :
    await bot.add_cog(Music(bot), guilds=(discord.Object(id=1033811091828002817)))