import os
import discord
import time

from discord import app_commands
from discord.ext import tasks, commands
from dotenv import load_dotenv

from database.db import Database

# Charge the environment variables
load_dotenv()

# Bot instance
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# DB instance
db = Database()

# Events
@bot.event
async def on_ready():
    """_summary_: Event that triggers when the bot is ready to serve.
    """
    print(f'{bot.user} ready to serve!')
    await bot.change_presence(activity=discord.Game(name="Kweh!"))
    server_updates = bot.get_channel(int(os.getenv("SERVER_UPDATES_CHANNEL_ID")))

    # if server_updates:
    #     await server_updates.send("¡Kweh! I'm ready to serve!")

    try:
        # Sync the commands
        await bot.tree.sync()
        print("Commands synchronized.")
    except Exception as e:
        print(f"Error on syncing commands: {e}")


    check_birthdays.start()

# Tasks
@tasks.loop(hours=24)
async def check_birthdays():
    """_summary_: Task that checks the birthdays of the users on that day.
    """
    
    pass


#Slash commands
## General
@bot.tree.command(name="ping", description="Check the bot's latency.")
async def ping(interaction: discord.Interaction):
    """_summary_: Check the bot's latency.

    Args:
        interaction (discord.Interaction): 
    """
    start_time = time.perf_counter()
    
    await interaction.response.send_message("Pong!")

    end_time = time.perf_counter()
    elapsed_time = (end_time - start_time) * 1000 # in milliseconds

    print(f"Latency: {elapsed_time:.2f}ms")


## Birthdays
@bot.tree.command(name="birthday_add", description="Register a birthday.")
async def birthday_add(interaction: discord.Interaction, day: int, month: int):
    """_summary_: Register a birthday if the user doesn't have one. If it does, it sends an informative message.

    Args:
        interaction (discord.Interaction): 
        day (int): Day of the birthday.
        month (int): Month of the birthday.
    """
    user_id = interaction.user.id
    try:
        existing = await db.fetchrow("SELECT * FROM users WHERE discord_id = $1", user_id)
        if existing:
            await db.execute("UPDATE users SET bday_day = $1, bday_month = $2 WHERE discord_id = $3", day, month, user_id)
            message = f"Birthday updated successfully to {day}/{month}!"
        else:
            await db.execute("INSERT INTO users (discord_id, bday_day, bday_month) VALUES ($1, $2, $3)", user_id, day, month)
            message = f"Birthday registered successfully on {day}/{month}!"
    finally:
        await db.close()
    
    await interaction.response.send_message(message)

@bot.tree.command(name="birthday_remove", description="Remove a birthday.")
async def birthday_remove(interaction: discord.Interaction):
    """_summary_: Searches for the birthday of the user and removes it. If it doesn't exist, it sends an informative message.

    Args:
        interaction (discord.Interaction): 
    """
    
    user_id = interaction.user.id
    try:
        existing = await db.fetchrow("SELECT * FROM users WHERE discord_id = $1", user_id)
        if existing:
            await db.execute("UPDATE users SET bday_day = NULL, bday_month = NULL WHERE discord_id = $1", user_id)
            message = "Birthday removed successfully!"
        else:
            message = "You don't have a birthday registered."
    finally:
        await db.close()
    
    await interaction.response.send_message(message)

## Reminders
@bot.tree.command(name="remember_add", description="Create a reminder.")
async def remember_add(interaction: discord.Interaction, mensaje: str, fecha: str, canal: discord.TextChannel, periodicidad: int):
    # Lógica para crear un recordatorio
    await interaction.response.send_message(f"Recordatorio creado: {mensaje}")


## Raid events
@bot.tree.command(name="raid_event_add", description="Create a raid event.")
async def raid_event_add(interaction: discord.Interaction, evento: str, contenido: str, fecha: str):
    # Lógica para crear un evento de raid
    await interaction.response.send_message(f"Evento de raid creado: {evento}")


# Run the bot
bot.run(os.getenv('DISCORD_TOKEN'))