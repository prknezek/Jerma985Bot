import discord
from discord.ext import tasks, commands
from apikeys import *
from twitchAPI.twitch import Twitch
import requests

# authentication w/ Twitch API
client_id = TWITCH_CLIENT_ID
client_secret = TWITCH_CLIENT_SECRET_ID
twitch = Twitch(client_id, client_secret)
twitch.authenticate_app([])
TWITCH_STREAM_API_ENDPOINTS_V5 = "https://api.twitch.tv/kraken/streams/{}"
API_HEADERS = {
    'Client-ID' : client_id,
    'Accept' : 'application/vnd.twitchtv.v5+json'
}

# returns true if streamer is online and false if not online
def check_user(user) :
    try:
        userid = twitch.get_users(logins=[user])['data'][0]['id']
        url = TWITCH_STREAM_API_ENDPOINTS_V5.format(userid)
        try :
            req = requests.Session().get(url, headers=API_HEADERS)
            jsondata = req.json()
            if 'stream' in jsondata :
                if jsondata['stream'] is not None :
                    return True
                else :
                    return False
        except Exception as e :
            print("Error checking user: ", e)
            return False
    except IndexError :
        return False

class Livestream(commands.Cog) :
    def __init__(self, bot: commands.Bot) :
        self.bot = bot

    @commands.Cog.listener()
    # when the bot is ready to start receiveing commands it will execute this function
    async def on_ready(self):
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

            print("checking status")
            # checks every minute to see if jerma goes live
            if status :
                # check to see if notification for stream was already sent out to server
                messages = [message async for message in channel.history(limit=50)]
                # if no messages in channel then send live message
                if len(messages) == 0 :
                    await channel.send(
                        f":red_circle: **LIVE**\nJerma985 is live on Twitch!"
                        f"\nhttps://www.twitch.tv/jerma985"
                        f"\n@everyone"
                    )
                else : # if messages in channel, detect whether or not to delete them
                    async for message in channel.history(limit=50) :
                        # if message was sent out then break
                        if "Jerma985 is live on Twitch!" in message.content :
                            break
                        # sends live message if it wasn't sent out yet
                        else :
                            await channel.send(
                                f":red_circle: **LIVE**\nJerma985 is live on Twitch!"
                                f"\nhttps://www.twitch.tv/jerma985"
                                f"@everyone"
                            )
            else : # if they aren't live:
                async for message in channel.history(limit=200) :
                    if "Jerma985 is live on Twitch!" in message.content :
                        await message.delete()

            # if jerma is live change status
            if status :
                await self.bot.change_presence(status=discord.Status.online, 
                activity=discord.Streaming(name=stream_name, url="https://www.twitch.tv/jerma985"))
            else :
                await self.bot.change_presence(status=discord.Status.online, 
                activity=discord.CustomActivity(name="test", emoji=":red_circle:"))
        
        # starts the loop to scan for streaming activity
        live_notifs_loop.start()
        # print statement for when bot is ready
        print("Livestream Cog Loaded")

async def setup(bot: commands.Bot) :
    await bot.add_cog(Livestream(bot), guilds=(discord.Object(id=1033811091828002817)))