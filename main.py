import discord
from discord.ext import commands
from apikeys import * # imports variables from apikeys.py

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

# run the bot after initializing all commands
bot.run(BOTTOKEN)
