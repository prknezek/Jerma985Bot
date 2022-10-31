import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions

class Admin(commands.Cog) :
    def __init__(self, bot: commands.Bot) :
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self) :
        print("Admin Cog Loaded")

    @commands.command()
    @has_permissions(kick_members=True) # checks if user running bot command has permission to kick members
    # member is user to be kicked, reason is reason why they were kicked
    async def kick(self, ctx, member: discord.Member, *, reason=None) :
        await member.kick(reason=reason)
        await ctx.send(f'User {member} has been kicked')
        
    @kick.error # if user doesn't have permission to kick members
    async def kick_error(self, ctx, error) :
        if isinstance(error, commands.MissingPermissions) :
            await ctx.send("You dont have permission to kick")

    @commands.command()
    @has_permissions(ban_members=True) # checks if user running bot command has permission to ban members
    # member is user to be kicked, reason is reason why they were banned
    async def ban(self, ctx, member: discord.Member, *, reason=None) :
        await member.ban(reason=reason)
        await ctx.send(f'User {member} has been banned')

    @kick.error # if user doesn't have permission to ban members
    async def ban_error(self, ctx, error) :
        if isinstance(error, commands.MissingPermissions) :
            await ctx.send("You dont have permission to ban")

    @commands.command()
    async def dm(self, ctx, user: discord.Member, *, message) :
        # of type !dm @[user] [message]
        embed = discord.Embed(title=message)
        await user.send(embed=embed)

async def setup(bot: commands.Bot) :
    await bot.add_cog(Admin(bot), guilds=(discord.Object(id=1033811091828002817)))