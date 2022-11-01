import nextcord
from nextcord.ext import commands
from nextcord.ext.commands import has_permissions, MissingPermissions

class Admin(commands.Cog) :
    def __init__(self, bot: commands.Bot) :
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self) :
        print("Admin Cog Loaded")

    @commands.command()
    @has_permissions(kick_members=True) # checks if user running bot command has permission to kick members
    # member is user to be kicked, reason is reason why they were kicked
    async def kick(self, ctx, member: nextcord.Member, *, reason=None) :
        await member.kick(reason=reason)
        await ctx.send(f'User {member} has been kicked')
        
    @kick.error # if user doesn't have permission to kick members
    async def kick_error(self, ctx, error) :
        if isinstance(error, commands.MissingPermissions) :
            await ctx.send("You dont have permission to kick")

    @commands.command()
    @has_permissions(ban_members=True) # checks if user running bot command has permission to ban members
    # member is user to be kicked, reason is reason why they were banned
    async def ban(self, ctx, member: nextcord.Member, *, reason=None) :
        await member.ban(reason=reason)
        await ctx.send(f'User {member} has been banned')

    @kick.error # if user doesn't have permission to ban members
    async def ban_error(self, ctx, error) :
        if isinstance(error, commands.MissingPermissions) :
            await ctx.send("You dont have permission to ban")

    @commands.command()
    async def dm(self, ctx, user: nextcord.Member, *, message) :
        # of type !dm @[user] [message]
        embed = nextcord.Embed(title=message)
        await user.send(embed=embed)

    @commands.command(pass_context = True)
    @commands.has_permissions(manage_roles = True)
    # adds role to selected user
    async def add_role(self, ctx, user : nextcord.Member, *, role : nextcord.Role) :
        if role in user.roles :
            await ctx.send(f"{user.mention} already has the {role} role")
        else :
            await user.add_roles(role)
            await ctx.send(f"Added {role} role to {user.mention}")

    # error check if user does not have permission
    @add_role.error
    async def role_error(self, ctx, error) :
        if isinstance(error, commands.MissingPermissions) :
            await ctx.send("You do not have permission to use this command")

    @commands.command(pass_context = True)
    @commands.has_permissions(manage_roles = True)
    # removes role from selected user
    async def remove_role(self, ctx, user : nextcord.Member, *, role : nextcord.Role) :
        if role in user.roles :
            await user.remove_roles(role)
            await ctx.send(f"Removed {role} from {user.mention}")
        else :
            await ctx.send(f"{user.mention} doesn't have the {role} role")

    # error check if user does not have permission
    @add_role.error
    async def remove_roll_error(self, ctx, error) :
        if isinstance(error, commands.MissingPermissions) :
            await ctx.send("You do not have permission to use this command")

async def setup(bot: commands.Bot) :
    bot.add_cog(Admin(bot))