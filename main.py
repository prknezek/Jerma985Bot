import asyncio
import os

import nextcord
from nextcord.ext import commands

from apikeys import *  # imports variables from local apikeys.py

intents = nextcord.Intents.all() # make sure commands work
intents.members = True
intents.voice_states = True
COMMAND_PREFIX = '!' # initialize bot with command prefix '!' (OUTDATED with nextcord but still required)
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

@bot.event
async def on_ready() :
    print("Jerma Bot Online")

# current test server
serverId = 1033811091828002817

# -------------------------------- cog loading ------------------------------- #
async def load() :
    for filename in os.listdir("Jerma985Bot/cogs") :
        if filename.endswith('.py') :
            print(f"Loading {filename[:-3]}")
            bot.load_extension(f"cogs.{filename[:-3]}")

loop = asyncio.get_event_loop()

async def main() :
    await load()
    await bot.start(BOTTOKEN)

# using asyncio to run bot and load cogs
try:
    asyncio.ensure_future(main())
    loop.run_forever()
except KeyboardInterrupt:
    loop.run_until_complete(bot.close())
finally :
    loop.close()