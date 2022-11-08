import nextcord
from nextcord.ext import commands
from nextcord import Interaction
from pydealer import Deck, Stack, Card
import pydealer
from PIL import Image

class Blackjack(commands.Cog) :
    def __init__(self, bot : commands.Bot) :
        self.bot = bot
    
    serverId = 1033811091828002817

    @commands.Cog.listener()
    async def on_ready(self) :
        print("BlackJack Cog Loaded")

    @nextcord.slash_command(name="blackjack", description="Play blackjack with Mr. Green", guild_ids=[serverId])
    async def black_jack(self, interaction : Interaction) :
        mr_green_url = "https://static.wikia.nocookie.net/jerma-lore/images/2/25/MrGreen_RosterFace.png/revision/latest/top-crop/width/360/height/360?cb=20210426041715"
        
        embed = nextcord.Embed(title="Blackjack")
        

        deck = Deck(jokers=False, rebuild=True, re_shuffle=True)
        deck.shuffle()
        card = deck.deal()
        
        card_name = str(card).replace(" ", "_").lower() + ".png"
        print(card_name + " cards left: " + str(len(deck)))

        card_file = nextcord.File(f"./cogs/resources/PNG-cards-1.3/{card_name}", filename="card.png")

        im = Image.open(f"./cogs/resources/PNG-cards-1.3/{card_name}")
        print(im.format, im.size, im.mode)
        
        # gets the side of the card for merging with the next card
        box = (0, 0, 100, 726)
        region = im.crop(box)
        #region.show()

        embed = nextcord.Embed(title="Blackjack")
        embed.set_author(name= "Mr. Green's Casino", icon_url=mr_green_url)
        embed.set_image(url="attachment://card.png")
        await interaction.response.send_message(embed=embed, file=card_file)
    


    
def setup(bot: commands.Bot) :
    bot.add_cog(Blackjack(bot))