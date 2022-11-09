import nextcord
from nextcord.ext import commands
from nextcord import Interaction
from nextcord import SlashOption
from pydealer import Deck, Stack, Card
import pydealer
import os, sys
import asyncio
from io import BytesIO
from PIL import Image

mr_green_url = "https://static.wikia.nocookie.net/jerma-lore/images/2/25/MrGreen_RosterFace.png/revision/latest/top-crop/width/360/height/360?cb=20210426041715"
# merge two images together
def merge(im1, im2) :
    w = im1.size[0] + im2.size[0]
    h = max(im1.size[1], im2.size[1])
    im = Image.new("RGBA", (w, h))

    im.paste(im1)
    im.paste(im2, (im1.size[0], 0))

    return im

# returns first embed for blackjack when game is started
def on_blackjack_start(bet) :
    embed = nextcord.Embed(title="Blackjack", color=0x508f4a, description=f"Bet: {bet}")
    embed.set_author(name= "Mr. Green's Casino", icon_url=mr_green_url)
    return embed

# returns an updated embed w/ card
def embed_card_update(card_file_name, num_cards_dealt, bet) :
    embed = nextcord.Embed(title="Blackjack", color=0x508f4a, description=f"Bet: {bet}")
    embed.set_author(name= "Mr. Green's Casino", icon_url=mr_green_url)

    im = Image.open(f"./cogs/resources/PNG-cards-1.3/{card_file_name}")
    # gets the side of the card for merging with the next card
    box = (100 * (num_cards_dealt - 1), 0, 100 * num_cards_dealt, 726)
    region = im.crop(box)
    im = merge(region, im)

    # saving new image to nextcord.File for use in embed            
    bytes = BytesIO()
    im.save(bytes, "PNG")
    bytes.seek(0)
    card_file = nextcord.File(bytes, filename="card.png")

    # sets image of returned embed to new card image
    embed.set_image(url="attachment://card.png")
    # function returns card_file b/c it needs to be specifically updated in embed
    return (embed, card_file)

class Blackjack(commands.Cog) :
    def __init__(self, bot : commands.Bot) :
        self.bot = bot
    
    serverId = 1033811091828002817

    @commands.Cog.listener()
    async def on_ready(self) :
        print("BlackJack Cog Loaded")

    @nextcord.slash_command(name="blackjack", description="Play blackjack with Mr. Green", guild_ids=[serverId])
    async def black_jack(self, interaction : Interaction,
        bet: int = SlashOption(
            name="bet", description="Your bet for blackjack", required=True
        )
    ) :        
        # boolean for whether or not to end the game
        end_game = False
        num_cards_dealt = 0
        # initial creation of embed
        embed = on_blackjack_start(bet)
        msg = await interaction.response.send_message(embed=embed)
        # build deck
        deck = Deck(jokers=False, rebuild=True, re_shuffle=True)
        deck.shuffle()
        while not end_game :
            card = deck.deal()
            num_cards_dealt += 1
            card_file_name = str(card).replace(" ", "_").lower() + ".png"
            
            new_embed, card_file = embed_card_update(card_file_name, num_cards_dealt, bet)

            await asyncio.sleep(3)
            # update the sent message to include new card
            await msg.edit(embed=new_embed, file=card_file)
            end_game = True


    
def setup(bot: commands.Bot) :
    bot.add_cog(Blackjack(bot))