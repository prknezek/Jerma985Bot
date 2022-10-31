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
    
    @commands.command()
    async def embed(self, ctx) : # *** CAN CHANGE TO JERMA WIKI LINK 
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

async def setup(bot: commands.Bot) :
    await bot.add_cog(Admin(bot), guilds=(discord.Object(id=1033811091828002817)))