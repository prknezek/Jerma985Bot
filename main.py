import asyncio
import discord
import config
from discord.ext import commands
import os

from apikeys import * # imports variables from local apikeys.py

intents = discord.Intents.all() # make sure commands work
intents.members = True
COMMAND_PREFIX = '!' # initialize bot with command prefix '!'
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

@bot.event
async def on_ready() :
    print("Jerma Bot Online")

# cog loading
async def load() :
    for filename in os.listdir("./cogs") :
        if filename.endswith('.py') :
            print(f"Loading {filename[:-3]}")
            await bot.load_extension(f"cogs.{filename[:-3]}")

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
    