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

    @nextcord.slash_command(name="help", description="DMs user a list of commands", guild_ids=[serverId])
    async def help(self, interaction : Interaction) :

        embed = nextcord.Embed(title="Commands",
                               description="List of commands that you can use with the Jerma985 bot")
        embed.add_field(name="Greetings",
                        value="/hello - sends a hello message\n/skullface - sends x skullface emojis",
                        inline=False)
        embed.add_field(name="Youtube",
                        value="/youtube - sends a link to Jerma985's Youtube",
                        inline=False)
        embed.add_field(name="Twitch",
                        value="/twitch - sends a link to Jerma985's Twitch\n/rstream - sends a link to a random twitch stream",
                        inline=False)
        embed.add_field(name="TTS",
                        value="/join - joins your vc\n/leave - leaves your vc\n/jtts - plays a Jerma text-to-speech voice",
                        inline=False)
        embed.add_field(name="Birthday Cameo",
                        value="/birthday-message - sends a personalized Jerma985 birthday message\n/birthday-supported-names - sends a dm with a list of supported names for the birthday message",
                        inline=False)        
        embed.add_field(name="Data",
                        value="/store-info - stores info into a database (per user)\n/retrieve-info - retrieves stored info\n/balance - retrieves user's balance",
                        inline=False)
        embed.add_field(name="Mr. Green Games",
                        value="/bombtiles - play bomb tiles with Mr. Green\n/slots - play slots with Mr. Green\n/blackjack-simplified - play a simplified version of blackjack with Mr. Green",
                        inline=False)
        

        await interaction.user.send(embed=embed)
        return await interaction.send("Sent! Check your DMs.", ephemeral=True)

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