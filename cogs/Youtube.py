
from googleapiclient.discovery import build
import discord
from discord.ext import commands, tasks
from apikeys import *

# building base youtube api
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
# channel ids necessary for YoutubeAPI
j2_youtube_id = "UCL7DDQWP6x7wy0O6L5ZIgxg"
j985_youtube_id = "Jerma985"

class Youtube(commands.Cog) :
    def __init__(self, bot: commands.Bot) :
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) :
        # detects when a new youtube video is released
        @tasks.loop(minutes=1)
        async def yt_update():
            # publication activity req
            j2_publication_req = youtube.activities().list(part = "snippet", channelId = j2_youtube_id)
            j2_publication_res = j2_publication_req.execute()
            # date the video was published
            j2_video_published = j2_publication_res['items'][0]['snippet']['publishedAt']
            # formatting publication date
            format_index = j2_video_published.index("T")
            j2_video_published = j2_video_published[:format_index]

            # most recent video req
            j2_content_req = youtube.activities().list(part = "contentDetails", channelId = j2_youtube_id)            
            j2_content_res = j2_content_req.execute()
            # most recent video id
            j2_video_id = j2_content_res['items'][0]['contentDetails']['upload']['videoId']
            # link to the selected video
            link = f"https://www.youtube.com/watch?v={j2_video_id}"
            
            channel = await self.bot.fetch_channel(1036744556156309554)
            # all messages in discord channel (limit=50)
            messages = [message async for message in channel.history(limit=50)]
            # if message is not sent in channel then send message
            if len(messages) == 0 :
                await channel.send(
                        f"@everyone, **Jerma985** just posted a video!"
                        f"\n{link}"
                        f"\n***({j2_video_published})***"
                )
            else :
                async for message in messages :
                    if link not in message.content :
                        await channel.send(
                            f"@everyone, **Jerma985** just posted a video!"
                            f"\n{link}"
                            f"\n***({j2_video_published})***"
                        )
                    else :
                        pass

        yt_update.start()
        print("Youtube Cog Loaded")
        
    @commands.command()
    async def youtube(self, ctx) :
        await ctx.send("https://youtube.com/2ndJerma")

async def setup(bot: commands.Bot) :
    await bot.add_cog(Youtube(bot), guilds=(discord.Object(id=1033811091828002817)))