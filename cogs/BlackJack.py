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
import PIL
from nextcord import Message

# --------------------------------- global vars --------------------------------- #
MR_GREEN_URL = "https://static.wikia.nocookie.net/jerma-lore/images/2/25/MrGreen_RosterFace.png/revision/latest/top-crop/width/360/height/360?cb=20210426041715"
TABLE_WIDTH = 500
TABLE_HEIGHT = 330
VERTICAL_PADDING = 10

# --------------------------------- dropdown options --------------------------------- #
class BlackjackDropdown(nextcord.ui.Select) :
    def __init__(self) :
        select_options = [nextcord.SelectOption(label="Hit", value=0, description="Get another card from the dealer"),
                          nextcord.SelectOption(label="Stand", value=1, description="Keep your hand")]
        super().__init__(placeholder="Options:", min_values=1, max_values=1, options=select_options)

    async def callback(self, interaction : Interaction) :
        print("callback self.values " + self.values[0])
        self.view.view_callback(valParam = self.values[0])
        return self.values[0]

# --------------------------------- dropdown display --------------------------------- #
class BlackJackDropdownView(nextcord.ui.View) :
    def __init__(self) :
        super().__init__()
        self.add_item(BlackjackDropdown())
    
    def view_callback(self, valParam) :
        self.val = valParam
        self.stop()

# --------------------------------- initial table creation --------------------------------- #
def create_table() :    
    table = Image.new("RGB", (TABLE_WIDTH, TABLE_HEIGHT))
    felt = Image.open(f"./cogs/resources/PNG-cards-1.3/felt.png")
    table.paste(felt)
    return table
# --------------------------------- resize cards to correct size --------------------------------- #
def resize_card(im, num_cards_dealt) :
    base_width = 85 + (10 * num_cards_dealt)
    hsize = 121
    return im.resize((base_width, hsize), PIL.Image.ANTIALIAS)

# --------------------------------- merge two cards into a pile --------------------------------- #
def merge(im1, im2) :
    w = im1.size[0] + im2.size[0]
    h = max(im1.size[1], im2.size[1])
    im = Image.new("RGBA", (w, h))

    im.paste(im1)
    im.paste(im2, (im1.size[0], 0))

    return im

# converts table to file for use in embed
def convert_to_file(im) :
    bytes = BytesIO()
    im.save(bytes, "PNG")
    bytes.seek(0)
    return nextcord.File(bytes, filename="table.png")

# --------------------------------- updates table image --------------------------------- #
def table_update(table : Image, card_name : str, num_player_cards : int, num_dealer_cards : int, is_player_card : bool, player_cards : Image, dealer_cards : Image) :
    # get each cards file name
    card_file_name = card_name.replace(" ", "_").lower() + ".png"
    big_card = Image.open(f"./cogs/resources/PNG-cards-1.3/{card_file_name}")
    # if one card on stack
    if num_player_cards == 1 :
        little_card = resize_card(big_card, num_player_cards)
    # more than 1 card will be in stack
    else :
        if is_player_card :
            box = (100 * (num_player_cards - 2), 0, 100 * (num_player_cards - 1), 726)
            region = player_cards.crop(box)
            big_card = merge(region, big_card)
            little_card = resize_card(big_card, num_player_cards)
        else :
            box = (100 * (num_dealer_cards - 2), 0, 100 * (num_dealer_cards - 1), 726)
            region = dealer_cards.crop(box)
            big_card = merge(region, big_card)
            little_card = resize_card(big_card, num_dealer_cards)

    # constants for each card
    CARD_WIDTH = little_card.width
    CARD_HEIGHT = little_card.height
    # if card belongs to player
    if is_player_card :
        card_location = (TABLE_WIDTH // 2 - CARD_WIDTH // 2, TABLE_HEIGHT - CARD_HEIGHT - VERTICAL_PADDING)
        table.paste(little_card, card_location)
    # if card belongs to dealer
    else :
        card_location = (TABLE_WIDTH // 2 - CARD_WIDTH // 2, VERTICAL_PADDING)
        table.paste(little_card, card_location)
    # return table
    return (table, big_card)

# --------------------------------- deals card --------------------------------- #
async def card_deal(table : Image, embed : nextcord.Embed, view : BlackJackDropdownView, deck : Deck, for_player : bool, num_player_cards : int, 
                    num_dealer_cards : int, dealer_card_image : Image, player_card_image : Image, hidden_card : bool, player_cards : list, dealer_cards : list,
                    player_value : int, dealer_value : int) :
    card_name = str(deck.deal())
    print(f"card that was dealt: {card_name}")
    card_value = get_card_value(card_name)

    if for_player :
        player_value += card_value
        num_player_cards += 1
    else :
        dealer_value += card_value
        num_dealer_cards += 1
    if hidden_card :
        hidden_card_name = card_name
        card_name = "back card"
    else :
        hidden_card_name = None

    table, card = table_update(table, card_name, num_player_cards, num_dealer_cards, for_player, player_card_image, dealer_card_image)
    table_file = convert_to_file(table)

    if for_player :
        player_card_image = card
        player_cards.append(card_name)
    else :
        dealer_card_image = card
        if card_name == "back card" :
            dealer_cards.append(hidden_card_name)
        else :
            dealer_cards.append(card_name)

    await asyncio.sleep(0.5)
    return (player_value, dealer_value, player_cards, dealer_cards, player_card_image, dealer_card_image, num_player_cards, num_dealer_cards, table_file, hidden_card_name)

# --------------------------------- gets value of card --------------------------------- #
def get_card_value(card : str) :

    if "10" not in card and card[0].isdigit() :
        card_value = int(card[0])
    elif "Ace" in card :
        card_value = 11
    else:
        card_value = 10
    return card_value

#def turnover_dealer_card(dealer_hidden_card : ) :


# --------------------------------- check if someone won --------------------------------- #
def check_for_win(player_value : int, dealer_value : int, bet : float, dealer_reveal_card : bool) :
    game_end = False
    payment = None
    # game is over if dealer is at 17 or over OR if player gets a blackjack and dealer does not have a blackjack
    if (dealer_value >= 17 or (dealer_value < 21 and player_value == 21)) and dealer_reveal_card:
        game_end = True
    # WIN CONDITIONS
    # player blackjack
    if player_value == 21 and dealer_value != 21:
        payment = round(bet * 2.5, 2)
    # player has lower value than dealer
    elif game_end and player_value < dealer_value :
        payment = 0
    # player and dealer have same value
    elif game_end and player_value == dealer_value :
        payment = bet
    # dealer busts and player did not (player doesnt have blackjack either)
    elif dealer_value > 21 and not player_value < 21 :
        payment = round(bet * 2, 2)
    # player busts
    elif player_value > 21 :
        payment = 0

    return (payment, game_end)

# --------------------------------- main Blackjack game --------------------------------- #
class Blackjack(commands.Cog) :
    def __init__(self, bot : commands.Bot) :
        self.bot = bot
    
    serverId = 1033811091828002817

    @commands.Cog.listener()
    async def on_ready(self) :
        print("BlackJack Cog Loaded")

    @nextcord.slash_command(name="blackjack", description="Play blackjack with Mr. Green", guild_ids=[serverId])
    async def black_jack(self, interaction : Interaction,
        bet: float = SlashOption(
            name="bet", description="Your bet for blackjack", required=True
        )
    ) :        
        # function variables
        game_over = False
        num_player_cards = 0
        num_dealer_cards = 0
        player_value = 0
        dealer_value = 0
        player_card_image = None
        dealer_card_image = None
        dealer_hidden_card_name = None
        dealer_reveal_card = False
        player_cards = []
        dealer_cards = []
        bet = round(bet, 2)

        # initial creation of embed (deal cards to dealer and player)
        view = BlackJackDropdownView()
        # build deck
        deck = Deck(jokers=False, rebuild=True, re_shuffle=True)
        deck.shuffle()
        # basic embed
        # CHANGE BET TO ${bet} has been withdrawn from {player}'s account!
        embed = nextcord.Embed(title="Blackjack", color=0x508f4a, description=f"**Bet: {bet}**\n**Get as close to 21 as you can without going over!**\nDealer stands on 17 or more\n**--------------------------------------------------------------------------------**\n**Blackjack** pays: **{3 * bet}**  Regular win pays **{2 * bet}**")
        embed.set_author(name= "Mr. Green's Casino", icon_url=MR_GREEN_URL)
        embed.set_image(url="attachment://table.png")

        table = create_table()
        # starting hand
        for i in range(4) :
                for_player = False
                hidden_card = False
                if i == 1:
                    hidden_card = True
                if i % 2 == 0 :
                    for_player = True
                player_value, dealer_value, player_cards, dealer_cards, player_card_image, dealer_card_image, num_player_cards, num_dealer_cards, table_file, hidden_card_name = await card_deal(table, embed, view, deck, for_player, num_player_cards, num_dealer_cards, dealer_card_image, player_card_image, hidden_card, player_cards, dealer_cards, player_value, dealer_value)
                if hidden_card_name != None :
                    dealer_hidden_card_name = hidden_card_name
                if i == 0 :
                    msg = await interaction.send(embed=embed, file=table_file)
                else :
                    if i == 3:
                        await msg.edit(embed=embed, view=view, file=table_file)
                    else :
                        await msg.edit(embed=embed, file=table_file)        
        while not game_over :   
            # wait for decision from player
            print("waiting for player...")
            await view.wait()
            
            choice = int(view.val)
            print("player chose: " + str(choice) + " " + str(type(choice)))

            #view = BlackJackDropdownView()

            # player stands
            if choice == 1 :
                dealer_reveal_card = True
            
            # player hits
            elif choice == 0 :
                for_player = True
                hidden_card = False
                print("running hit command")
                player_value, dealer_value, player_cards, dealer_cards, player_card_image, dealer_card_image, num_player_cards, num_dealer_cards, table_file, hidden_card_name = await card_deal(table, embed, view, deck, for_player, num_player_cards, num_dealer_cards, dealer_card_image, player_card_image, hidden_card, player_cards, dealer_cards, player_value, dealer_value)

            # debugging
            for card in player_cards :
                print (card)
            for card in dealer_cards :
                print (card)

            print(player_value)
            print(dealer_value)
            
            print(f"value = {view.val}")
            print("made it past wait")

            payment, game_over = check_for_win(player_value, dealer_value, bet, dealer_reveal_card)
            game_over = True

        embed = nextcord.Embed(title="Payment", color=0x508f4a, description=f"**${payment}** has been **deposited** to stealthhemu#3654's account!\nTotal Balance: **$0.00**")
        embed.set_author(name= "Mr. Green's Casino", icon_url=MR_GREEN_URL)
        embed.set_image(None)
        await msg.edit(embed=embed, view=None)

def setup(bot: commands.Bot) :
    bot.add_cog(Blackjack(bot))