import asyncio
import nextcord
from nextcord.ext import commands
from nextcord import Interaction
import os

from apikeys import * # imports variables from local apikeys.py

intents = nextcord.Intents.all() # make sure commands work
intents.members = True
COMMAND_PREFIX = '!' # initialize bot with command prefix '!'
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

@bot.event
async def on_ready() :
    print("Jerma Bot Online")

serverId = 1033811091828002817

@bot.slash_command(name ="test", description = "introduction to slash commands", guild_ids=[serverId])
async def test(interaction : Interaction) :
    await interaction.response.send_message("Hello")

# cog loading
async def load() :
    for filename in os.listdir("./cogs") :
        if filename.endswith('.py') :
            print(f"Loading {filename[:-3]}")
            bot.load_extension(f"cogs.{filename[:-3]}")

async def main() :
    await load()
    await bot.start(BOTTOKEN)

# using asyncio to run bot and load cogs
try :
    loop = asyncio.get_running_loop()
except RuntimeError :
    loop = None

if not (loop and loop.is_running()) :
    print("Starting new event loop")
    result = asyncio.run(main())
else:
    print('Async event loop already running.')
    