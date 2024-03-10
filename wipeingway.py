import dotenv
import os

#Discord dependencies
import discord
from discord import app_commands
from discord.ext import commands

#Bot instance
bot = commands.Bot(command_prefix="!", intents= discord.Intents.all())

#Tokenization from environment
dotenv.load_dotenv()
TOKEN = os.environ["DISCORD_TOKEN"]


#Bot on_ready welcome message
@bot.event
async def on_ready():
    print("Hola hola!")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")

    except Exception as e:
        print(f"Exception: {e}") 

#Bot function to say hello
@bot.tree.command(name="hello")
async def hello (interaction: discord.Interaction):
    await interaction.response.send_message(
        f"¿Como estás {interaction.user.mention}?\nFeliz wipe :rabbit:",
        ephemeral=True)

#Bot function to play ping pong
@bot.tree.command(name="ping")
async def ping (interaction: discord.Interaction):
    await interaction.response.send_message(
        f"pong!",
        ephemeral=True)

#Application init
bot.run(TOKEN)