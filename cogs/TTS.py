from io import BytesIO
import json
import time
import aiohttp
import asyncio
import nextcord
from nextcord import SlashOption
from nextcord.ext import commands
from nextcord import Interaction
from datetime import datetime, timezone, timedelta
import subprocess
import tempfile
from apikeys import *
import os

guild_to_voice_client = dict()
# terminates bot after not being used for 5 minutes
async def terminate_stale_voice_connections():
    while True:
        await asyncio.sleep(5)
        for k in list(guild_to_voice_client.keys()):
            v = guild_to_voice_client[k]
            voice_client, last_used = v
            if datetime.utcnow() - last_used > timedelta(minutes=5):
                await voice_client.disconnect()
                guild_to_voice_client.pop(k)

def _context_to_voice_channel(interaction) :
    # returns channel that user is in if user is in a channel
    return interaction.user.voice.channel if interaction.user.voice else None

# if creates and returns a voice client if there is none
# returns voice client if it already exists
async def _get_or_create_voice_client(interaction) :
    # whether or not bot has joined the voice channel
    joined = False
    # if the guild id is in the dict
    if interaction.guild.id in guild_to_voice_client :
        # voice client is 
        voice_client, last_used = guild_to_voice_client[interaction.guild.id]
    else :
        # gets voice channel
        voice_channel = _context_to_voice_channel(interaction)
        if voice_channel is None :
            voice_client = None
        else :
            # if voice channel exists, bot joins the voice channel
            voice_client = await voice_channel.connect()
            joined = True
            print("connected to channel")
    # returns tuple of the voice client and joined status
    return (voice_client, joined)

API_ROOT = "https://api.uberduck.ai"

# API CALL TO UBERDUCK W/ ERROR CHECKING
async def query_uberduck(text, voice="jerma985") :
    max_time = 60
    async with aiohttp.ClientSession() as session :
        url = f"{API_ROOT}/speak"
        data = json.dumps(
            {
                "speech" : text,
                "voice" : voice,
            }
        )
        start = time.time()
        async with session.post(
            url,
            data=data,
            auth=aiohttp.BasicAuth(UBERDUCK_TTS_PUBLIC_KEY, UBERDUCK_TTS_SECRET_KEY),
        ) as r :
            if r.status != 200 :
                raise Exception("Error synthesizing speech", await r.json())
            uuid = (await r.json())["uuid"]
        while True :
            if time.time() - start > max_time :
                raise Exception("Request timed out")
            await asyncio.sleep(1)
            status_url = f"{API_ROOT}/speak-status"
            async with session.get(status_url, params={"uuid" : uuid}) as r :
                if r.status != 200 :
                    continue
                response = await r.json()
                if response["path"] :
                    async with session.get(response["path"]) as r :
                        return BytesIO(await r.read())

class TTS(commands.Cog) :
    def __init__(self, bot : commands.Bot) :
        self.bot = bot

    serverId = 1033811091828002817

    @commands.Cog.listener()
    async def on_ready(self) :
        print("TTS Cog Loaded")

    @nextcord.slash_command(name = "join", description="Allows bot to join voice chat", guild_ids=[serverId])
    async def join_channel(self, interaction : Interaction) :
        # get the voice client
        voice_client, joined = await _get_or_create_voice_client(interaction)
        # if user is not in a channel
        if voice_client is None :
            await interaction.response.send_message("You're not in a voice channel", ephemeral=True)
        # if user in voice channel and the voice_client's selected channel is not the id of the user's voice channel
        # (mostly run when bot is already in a channel with no users and the join command is run again from a different channel)
        elif interaction.user.voice and voice_client.channel.id != interaction.user.voice.channel.id :
            old_channel_name = voice_client.channel.name
            # disconnect from old channel
            await voice_client.disconnect()
            voice_client = await interaction.user.voice.channel.connect()
            new_channel_name = voice_client.channel.name
            guild_to_voice_client[interaction.guild.id] = (voice_client, datetime.now(timezone.utc))
            await interaction.response.send_message(f"Switched from #{old_channel_name} to #{new_channel_name}")
        else :
            await interaction.response.send_message("Connected to voice channel")
            # add voice client to dict with time it joined
            guild_to_voice_client[interaction.guild.id] = (voice_client, datetime.now(timezone.utc))
        
    @nextcord.slash_command(name = "leave", description="Kicks bot from voice channel", guild_ids=[serverId])
    async def leave_channel(self, interaction : Interaction) :
        if interaction.guild.id in guild_to_voice_client :
            # gets rid of voice client from dictionary
            voice_client, _ = guild_to_voice_client.pop(interaction.guild.id)
            # disconnects bot from voice channel
            await voice_client.disconnect()
            await interaction.send("Disconnected from voice channel")
        else :
            # sends if bot is not in a channel
            await interaction.send("Bot is not connected to a voice channel", ephemeral=True)

    @nextcord.slash_command(name = "jtts", description="Text to Speech in Jerma's voice", guild_ids=[serverId])
    async def jerma_tts(self, interaction : Interaction,
        speech : str = SlashOption(
            name="speech", description="Speech to synthesize", required=True
        ),
        voice : str = SlashOption(
            required=False, name="voice", description="Voice to use for synthetic speech", default = "jerma985",
        )
    ) :
        voice_client, _ = await _get_or_create_voice_client(interaction)
        if voice_client :
            guild_to_voice_client[interaction.guild.id] = (voice_client, datetime.utcnow())
            await interaction.response.defer(ephemeral=True, with_message=True)
            audio_data = await query_uberduck(speech, voice)
            
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wav_f, tempfile.NamedTemporaryFile(suffix=".opus", delete=False) as opus_f :
                wav_f.write(audio_data.getvalue())
                wav_f.flush()
                print(opus_f.name)
                print(wav_f.name)
                # ---------CHECK_CALL DOES NOT FUNCTION PROPERLY---------
                wav_f.close()
                opus_f.close()
                subprocess.check_call(["ffmpeg", "-y", "-i", wav_f.name, opus_f.name])
                source = nextcord.FFmpegOpusAudio(wav_f.name)
                #source = nextcord.FFmpegOpusAudio(opus_f.name)
                voice_client.play(source, after=None)
                while voice_client.is_playing() :
                    await asyncio.sleep(0.5)
                await interaction.send("Sent an Uberduck message in vc")
        else :
            await interaction.send("You're not in a voice channel", ephemeral=True)


def setup(bot: commands.Bot) :
    bot.add_cog(TTS(bot))