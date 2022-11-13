import asyncio
from random import randint

import nextcord
import requests
from nextcord import Interaction, SlashOption
from nextcord.ext import commands
from PIL import Image

import cogs.BlackJack as blackjack
import cogs.Data as database
from cogs.Livestream import emote_images_url

MR_GREEN_URL = "https://static.wikia.nocookie.net/jerma-lore/images/2/25/MrGreen_RosterFace.png/revision/latest/top-crop/width/360/height/360?cb=20210426041715"

IMG_WIDTH = 470
IMG_HEIGHT = 60

class Slots(commands.Cog) :
    def __init__(self, bot : commands.Bot) :
        self.bot = bot

    serverId = 1033811091828002817

    @commands.Cog.listener()
    async def on_ready(self) :
        print("Slots Cog Loaded")

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
    bot.add_cog(Slots(bot))