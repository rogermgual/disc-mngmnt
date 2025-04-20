import os
import discord
import time
import datetime

from discord import app_commands
from discord.ext import tasks, commands
from dotenv import load_dotenv

from app.database.funcs import Database

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
    """
    Event that triggers when the bot is ready to serve.
    """
    print(f'{bot.user} ready to serve!')
    await bot.change_presence(activity=discord.Game(name="Kweh!"))
    server_updates = bot.get_channel(int(os.getenv("SERVER_UPDATES_CHANNEL_ID")))

    if server_updates:
        await server_updates.send("**¡Kweh! I'm ready to serve!**")

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
    """
    Check the birthdays of the users for the current week and send a message to the birthday channel.
    """
    today = datetime.date.today()
    if today.weekday() == 0:  # Lunes
        await announce_upcoming_birthdays()
    await announce_today_birthdays()


#Slash commands
## General
@bot.tree.command(name="ping", description="Check the bot's latency.")
async def ping(interaction: discord.Interaction):
    """Check the bot's latency.

    Args:
        interaction (discord.Interaction): 
    """
    print("Pinging...")
    start_time = time.perf_counter()
    
    await interaction.response.send_message("Pong!")

    end_time = time.perf_counter()
    elapsed_time = (end_time - start_time) * 1000 # in milliseconds

    print(f"Latency: {elapsed_time:.2f}ms")


## Birthdays
@bot.tree.command(name="birthday_add", description="Register a birthday.")
async def birthday_add(interaction: discord.Interaction, day: int, month: int):
    """Register a birthday if the user doesn't have one. If it does, it sends an informative message."""
    print("Registering birthday...")
    user_id = str(interaction.user.id)

    try:
        existing = await db.fetchrow("SELECT * FROM birthdays WHERE discord_id = $1", user_id)

        if existing:
            await db.execute(
                "UPDATE birthdays SET bday_day = $1, bday_month = $2 WHERE discord_id = $3",
                day, month, user_id
            )
            message = f"🎂 Birthday updated successfully to {day}/{month}!"
        else:
            await db.execute(
                "INSERT INTO birthdays (discord_id, bday_day, bday_month) VALUES ($1, $2, $3)",
                user_id, day, month
            )
            message = f"🎉 Birthday registered successfully on {day}/{month}!"

    except Exception as e:
        print(f"An error occurred: {e}")
        message = "❌ An error occurred while saving your birthday."

    await interaction.response.send_message(message)


@bot.tree.command(name="birthday_remove", description="Remove a birthday.")
async def birthday_remove(interaction: discord.Interaction):
    """Searches for the birthday of the user and removes it. If it doesn't exist, it sends an informative message.

    Args:
        interaction (discord.Interaction): 
    """
    print("Removing birthday...")
    user_id = interaction.user.id
    try:
        existing = await db.fetchrow("SELECT * FROM users WHERE discord_id = $1", user_id)
        if existing:
            await db.execute("UPDATE users SET bday_day = NULL, bday_month = NULL WHERE discord_id = $1", user_id)
            message = "Birthday removed successfully!"
        else:
            message = "You don't have a birthday registered."
    except Exception as e:
        print(f"An error occurred: {e}")
    
    await interaction.response.send_message(message)

async def announce_upcoming_birthdays():
    """
    Announces the birthdays for the upcoming week.
    """
    print("Checking upcoming birthdays...")
    today = datetime.date.today()
    start_week = today - datetime.timedelta(days=today.weekday())  # Monday
    end_week = start_week + datetime.timedelta(days=6)  # Sunday
    
    try:
        upcoming_birthdays = await db.fetch(
            """
            SELECT discord_id, bday_day, bday_month FROM users
            WHERE (bday_month = $1 AND bday_day >= $2) 
            OR (bday_month = $3 AND bday_day <= $4)
            OR (bday_month > $1 AND bday_month < $3)
            """,
            start_week.month, start_week.day, end_week.month, end_week.day
        )
        
        if upcoming_birthdays:
            channel = bot.get_channel(int(os.getenv("SERVER_UPDATES_CHANNEL_ID")))
            if channel:
                message = "🎉 **Birthdays this week!** 🎉\n"
                for user in upcoming_birthdays:
                    message += f"🎂 <@{user['discord_id']}> - {user['bday_day']}/{user['bday_month']}\n"
                await channel.send(message)
    
    except Exception as e:
        print(f"An error occurred: {e}")

async def announce_today_birthdays():
    """
    Check the birthdays of the users for the current day and send a message to the birthday channel.
    """
    print("Checking today's birthdays...")
    today = datetime.date.today()
    try:
        birthdays_today = await db.fetch(
            "SELECT discord_id FROM users WHERE bday_day = $1 AND bday_month = $2", today.day, today.month
        )
        
        if birthdays_today:
            channel = bot.get_channel(int(os.getenv("SERVER_UPDATES_CHANNEL_ID")))
            if channel:
                mentions = " ".join(f"<@{user['discord_id']}>" for user in birthdays_today)
                await channel.send(f"🎂 @here Happy Birthday {mentions}! 🎉 Have an amazing day! 🎈")
    
    except Exception as e:
        print(f"An error occurred: {e}")


@bot.tree.command(name="test_birthdays", description="Force the birthday announcement tasks.")
async def test_birthdays(interaction: discord.Interaction):
    """
    Forces the execution of the birthday announcement tasks.
    """
    await interaction.response.send_message("Testing birthday announcements...")

    print("🔍 Forcing today's birthday check...")
    await announce_today_birthdays()

    print("🔍 Forcing weekly birthday check...")
    await announce_upcoming_birthdays()


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