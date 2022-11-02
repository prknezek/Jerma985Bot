import nextcord
from nextcord.ext import commands
from nextcord import Interaction
from nextcord.ext.commands import has_permissions, MissingPermissions

class Admin(commands.Cog) :
    def __init__(self, bot: commands.Bot) :
        self.bot = bot
    
    serverId = 1033811091828002817

    @commands.Cog.listener()
    async def on_ready(self) :
        print("Admin Cog Loaded")

    @nextcord.slash_command(name="kick", description="kicks user", guild_ids=[serverId])
    @has_permissions(kick_members=True) # checks if user running bot command has permission to kick members
    # member is user to be kicked, reason is reason why they were kicked
    async def kick(self, interaction : Interaction, member: nextcord.Member, *, reason=None) :
        await member.kick(reason=reason)
        await interaction.send(f'User {member} has been kicked')
        
    @kick.error # if user doesn't have permission to kick members
    async def kick_error(self, interaction : Interaction, error) :
        if isinstance(error, commands.MissingPermissions) :
            await interaction.send("You dont have permission to kick")

    @nextcord.slash_command(name="ban", description="bans user", guild_ids=[serverId])
    @has_permissions(ban_members=True) # checks if user running bot command has permission to ban members
    # member is user to be kicked, reason is reason why they were banned
    async def ban(self, interaction : Interaction, member: nextcord.Member, *, reason=None) :
        await member.ban(reason=reason)
        await interaction.send(f'User {member} has been banned')

    @kick.error # if user doesn't have permission to ban members
    async def ban_error(self, interaction : Interaction, error) :
        if isinstance(error, commands.MissingPermissions) :
            await interaction.send("You dont have permission to ban")

    @nextcord.slash_command(name="dm", description="dms user", guild_ids=[serverId])
    async def dm(self, interaction : Interaction, user: nextcord.Member, *, message) :
        # of type !dm @[user] [message]
        embed = nextcord.Embed(title=message)
        await user.send(embed=embed)

    @nextcord.slash_command(name="add_role", description="adds role to user", guild_ids=[serverId])
    @commands.has_permissions(manage_roles = True)
    # adds role to selected user
    async def add_role(self, interaction : Interaction, user : nextcord.Member, *, role : nextcord.Role) :
        if role in user.roles :
            await interaction.send(f"{user.mention} already has the {role} role")
        else :
            await user.add_roles(role)
            await interaction.send(f"Added {role} role to {user.mention}")

    # error check if user does not have permission
    @add_role.error
    async def role_error(self, interaction : Interaction, error) :
        if isinstance(error, commands.MissingPermissions) :
            await interaction.send("You do not have permission to use this command")

    @nextcord.slash_command(name="remove_role", description="removes role from user", guild_ids=[serverId])
    @commands.has_permissions(manage_roles = True)
    # removes role from selected user
    async def remove_role(self, interaction : Interaction, user : nextcord.Member, *, role : nextcord.Role) :
        if role in user.roles :
            await user.remove_roles(role)
            await interaction.send(f"Removed {role} from {user.mention}")
        else :
            await interaction.send(f"{user.mention} doesn't have the {role} role")

    # error check if user does not have permission
    @add_role.error
    async def remove_roll_error(self, interaction : Interaction, error) :
        if isinstance(error, commands.MissingPermissions) :
            await interaction.send("You do not have permission to use this command")

def setup(bot: commands.Bot) :
    bot.add_cog(Admin(bot))