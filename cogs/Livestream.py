import asyncio
from random import randint

import nextcord
import requests
from nextcord import Interaction, SlashOption
from nextcord.ext import commands, tasks
from twitchAPI.twitch import Twitch
from PIL import Image

import cogs.Data as database
import cogs.BlackJack as blackjack

from apikeys import *

MR_GREEN_URL = "https://static.wikia.nocookie.net/jerma-lore/images/2/25/MrGreen_RosterFace.png/revision/latest/top-crop/width/360/height/360?cb=20210426041715"

IMG_WIDTH = 470
IMG_HEIGHT = 60

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

# ------------------------------- Emote Request ------------------------------ #
CHANNEL_ID = 23936415
emotereq = requests.get(f"https://api.twitch.tv/helix/chat/emotes?broadcaster_id={CHANNEL_ID}", headers=API_HEADERS)
emotejson = emotereq.json()['data']
emote_images_url = []
slots_emotes_ids = ["156952", "1279967", "160423", "87845", "1279994", "1279975", "79428", "1096266", "279998"]
for img in emotejson :
    # getting image url and changing to dark mode then adding to list of images
    img_url = img['images']['url_2x']
    dark_img_url = img_url.replace("light", "dark")
    # if img_url is one of the ones we want, add image to list
    for id in slots_emotes_ids :
        if id in dark_img_url :
            emote_images_url.append(dark_img_url)

for img in emote_images_url :
    print(img)

print(f"-------------- Num of emotes: {len(emote_images_url)} --------------")


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
                    if "is live on Twitch!" in message.content :
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

    # gives user a random broadcast from the past 60 days
    # twitch only stores broadcasts for 60 days
    @nextcord.slash_command(name="rstream", description="retrieves a random Jerma985 stream", guild_ids=[serverId])    
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
    
    @nextcord.slash_command(name="slots", description="A slots game", guild_ids=[serverId])
    async def slots_game(self, interaction : Interaction, starting_bet:float = SlashOption(name="bet", description="Amount of money to bet")) :
        
        # ---------------------- check if starting_bet is valid ---------------------- #
        starting_bet = database.normal_round(starting_bet, 2)        
        if starting_bet <= 0.00:
            return await interaction.send("What, you think I'm an idiot?! - Mr. Green", ephemeral=True)

        # ---------------- check balance and take money away from user --------------- #
        try:
            user_balance_raw = database.retrieveData(interaction.guild.id, interaction.user, ['MONEY'])[0]
        except:
            return await interaction.send("Uh oh! I couldn't connect to the database.")
        if user_balance_raw[0] == '$':
            user_balance = float(user_balance_raw[1:])
        else:
            user_balance = float(user_balance_raw)
        if user_balance < starting_bet:
            return await interaction.send("You're too broke to play! - Mr. Green", ephemeral=True)
        user_balance -= starting_bet
        database.storeData(interaction.guild.id, interaction.user, {'MONEY': str(user_balance)})
        

        felt_img = Image.open("./cogs/resources/transparentbg.png")
        felt_edit = Image.new("RGBA", (IMG_WIDTH, IMG_HEIGHT))
        felt_edit.paste(felt_img)
        felt_file = blackjack.convert_to_file(felt_edit)

        # ----------------------------- send instructions ---------------------------- #
        embed = nextcord.Embed(title="Slots", color=0x508f4a)
        embed.set_author(name= "Mr. Green's Casino", icon_url=MR_GREEN_URL)
        embed.add_field(name="If the pictures line up, you could win big! Good luck!\n-----------------------------------------------------------", 
                        value="**${:.2f}** has been **withdrawn** from {}'s account!".format(starting_bet, str(interaction.user)), inline=False)
        embed.add_field(name="Slot 1", value="rolling...", inline=True)
        embed.add_field(name="Slot 2", value="rolling...", inline=True)
        embed.add_field(name="Slot 3", value="rolling...", inline=True)
        embed.set_image(url="attachment://table.png")
        message = await interaction.send(embed=embed, file=felt_file)

        imgIndexList = []
        xcords = [0, 150, 316]
        for fieldIndex in range(1,len(embed.fields)):

            await asyncio.sleep(fieldIndex/2+0.5)
            imgIndex = randint(0,4)
            imgIndexList.append(imgIndex)
            embed.remove_field(fieldIndex)
            embed.insert_field_at(fieldIndex, name=f"Slot {fieldIndex}", value=f"{imgIndex}", inline=True)            
            
            #do some more file shit 
            coordinates = (xcords[fieldIndex-1], 0)
            print(coordinates)

            felt_img = Image.open("./cogs/resources/transparentbg.png")
            #felt_edit = Image.new("RGBA", (IMG_WIDTH, IMG_HEIGHT))

            slot_img = Image.open(requests.get(emote_images_url[imgIndex], stream=True).raw)
            felt_edit.paste(slot_img, coordinates)
            felt_file = blackjack.convert_to_file(felt_edit)

            await message.edit(embed=embed, file=felt_file)

        await asyncio.sleep(0.7)

        # calculate payout
        payout = 0
        multiplier = 1
        if imgIndexList[0] == imgIndexList[1]:
            payout += starting_bet
            multiplier += imgIndexList[0]+3.5
        if imgIndexList[1] == imgIndexList[2]:
            payout += starting_bet
            multiplier += imgIndexList[1]+3.5
        payout *= multiplier

        # payout
        user_balance += payout
        database.storeData(interaction.guild.id, interaction.user, {'MONEY': str(user_balance)})
        embed = nextcord.Embed(title="Payment", color=0x508f4a, description="**${:.2f}** has been **deposited** to {}'s account!\nTotal Balance: **${:.2f}**".format(payout, str(interaction.user), user_balance))
        embed.set_author(name= "Mr. Green's Casino", icon_url=MR_GREEN_URL)
        return await interaction.send(embed=embed)


# export cog to bot
def setup(bot: commands.Bot) :
    bot.add_cog(Livestream(bot))