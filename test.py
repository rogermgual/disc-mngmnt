import discord
from discord import app_commands
from discord.ext import commands

bot = commands.Bot(command_prefix="!", intents= discord.Intents.all())

tmp = open(".credentials.txt", "r")
TOKEN = tmp.read()

@bot.event
async def on_ready():
    print("Bot is up!")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")

    except Exception as e:
        print(f"Exception: {e}") 

@bot.tree.command(name="hello")
async def hello (interaction: discord.Interaction):
    await interaction.response.send_message(
        f"Hey {interaction.user.mention}! This is an slash command",
        ephemeral=True)

@bot.tree.command(name="ping")
async def ping (interaction: discord.Interaction):
    await interaction.response.send_message(
        f"pong!",
        ephemeral=True)

bot.run(TOKEN)