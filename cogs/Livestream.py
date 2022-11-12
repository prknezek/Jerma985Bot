from random import randint

import nextcord
import requests
from nextcord import Interaction
from nextcord.ext import commands, tasks
from twitchAPI.twitch import Twitch

from apikeys import *

# authentication w/ Twitch API
client_id = TWITCH_CLIENT_ID
client_secret = TWITCH_CLIENT_SECRET_ID
twitch = Twitch(client_id, client_secret)
twitch.authenticate_app([])

body = {
    'client_id': client_id,
    'client_secret': client_secret,
    'grant_type': 'client_credentials'
}
r = requests.post('https://id.twitch.tv/oauth2/token', body)
keys = r.json()

TWITCH_STREAM_API_ENDPOINTS_V5 = "https://api.twitch.tv/helix/streams?user_login={}"
API_HEADERS = {
    'Client-ID' : client_id,
    'Authorization': 'Bearer ' + keys['access_token']
}

# returns true if streamer is online and false if not online
def check_user(user):
    try:
        url = TWITCH_STREAM_API_ENDPOINTS_V5.format(user)
        try :
            req = requests.get(url, headers=API_HEADERS)
            jsondata = req.json()
            if len(jsondata['data']) == 1 :
                return True
            else:
                return False           
        except Exception as e :
            print("Error checking user: ", e)
            return False
    except IndexError :
        return False

class Livestream(commands.Cog) :
    def __init__(self, bot: commands.Bot) :
        self.bot = bot

    serverId = 1033811091828002817

    @commands.Cog.listener()
    # when the bot is ready to start receiveing commands it will execute this function
    async def on_ready(self):
        # print statement for when bot is ready
        print("Livestream Cog Loaded")

        # live streaming detection
        @tasks.loop(minutes=1)
        async def live_notifs_loop() :
            # grabbing info from server
            guild = self.bot.get_guild(1033811091828002817)
            status = check_user("jerma985")
            channel = self.bot.get_channel(1036160854460215337)

            # getting twitch info
            broadcaster_info = twitch.get_users(user_ids=None, logins="jerma985")["data"][0]
            broadcaster_id = broadcaster_info['id']
            channel_info = twitch.get_channel_information(broadcaster_id=broadcaster_id)["data"][0]
            stream_name = channel_info["title"]

            print("checking stream status: {}".format(status))
            # checks every minute to see if jerma goes live
            if status :
                # check to see if notification for stream was already sent out to server
                messages = [message async for message in channel.history(limit=50)]
                # if no messages in channel then send live message
                if len(messages) == 0 :
                    await channel.send(
                        f":red_circle: **LIVE**\n@everyone, **Jerma985** is live on Twitch!"
                        f"\nhttps://www.twitch.tv/jerma985"
                    )
                else : # if messages in channel, detect whether or not to delete them
                    async for message in channel.history(limit=50) :
                        # if message was sent out then break
                        if "Jerma985 is live on Twitch!" in message.content :
                            break
                        # sends live message if it wasn't sent out yet
                        else :
                            await channel.send(
                                f":red_circle: **LIVE**\n@everyone, **Jerma985** is live on Twitch!"
                                f"\nhttps://www.twitch.tv/jerma985"
                            )
            else : # if they aren't live:
                async for message in channel.history(limit=200) :
                    if "Jerma985 is live on Twitch!" in message.content :
                        await message.delete()

            # if jerma is live change status
            if status :
                await self.bot.change_presence(status=nextcord.Status.online, 
                activity=nextcord.Streaming(name=stream_name, url="https://www.twitch.tv/jerma985"))
            else :
                await self.bot.change_presence(status=nextcord.Status.online, 
                activity=nextcord.CustomActivity(name="test", emoji=":red_circle:"))
        
        # starts the loop to scan for streaming activity
        live_notifs_loop.start()

    @nextcord.slash_command(name="rstream", description="retrieves a random Jerma985 stream", guild_ids=[serverId])
    # gives user a random broadcast from the past 60 days
    # twitch only stores broadcasts for 60 days
    async def rstream(self, interaction : Interaction):
        # gets broadcaster info
        broadcaster_info = twitch.get_users(user_ids=None, logins="jerma985")["data"][0]
        broadcaster_id = broadcaster_info['id']
        broadcaster_image = broadcaster_info['profile_image_url']
        twitch_url = "https://twitch.tv/jerma985"

        # gets all available past broadcasts
        past_broadcasts = twitch.get_videos(user_id=broadcaster_id)['data']
        video_num_index = len(past_broadcasts)-1 # index of last broadcast
        broadcast_index = randint(0, video_num_index) # generates a random number as the index for past broadcast

        print(f"-----{broadcast_index}-----")

        # grabs the random broadcast from data
        selected_broadcast = past_broadcasts[broadcast_index]
        # additional info for embed
        title = selected_broadcast['title']
        url = selected_broadcast['url']
        author = selected_broadcast['user_name']
        published = selected_broadcast['published_at']
        duration = selected_broadcast['duration']
        
        # formatting duration
        formattedDuration = ""
        for x in duration:
            if x.isnumeric():
                formattedDuration = formattedDuration + x
            else:
                formattedDuration = formattedDuration + x + " "
        duration = formattedDuration

        # formatting published
        format_index = published.index("T")
        published = published[:format_index]

        thumbnail = selected_broadcast['thumbnail_url']

        embed = nextcord.Embed(title="Random Stream", url=url, description=title, color=0x6441a5)
        
        embed.set_author(name=author, url=twitch_url, icon_url=broadcaster_image)
        
        # thumbnail
        #embed.set_thumbnail(url="https://static.wikia.nocookie.net/jerma-lore/images/9/91/Evil_Jerma.png")
        user = interaction.user.display_name
        embed.add_field(name="Duration:", value=duration, inline=True)
        embed.add_field(name="Published:", value=published, inline=True)
        embed.set_footer(text=f"Sent by: {user}")
        await interaction.send(embed=embed)

    @nextcord.slash_command(name="twitch", description="Sends a link to Jerma985's twitch", guild_ids=[serverId])
    async def twitch(self, interaction : Interaction) :
        await interaction.send("https://twitch.tv/jerma985")
        
# export cog to bot
def setup(bot: commands.Bot) :
    bot.add_cog(Livestream(bot))