import os
import discord
import time
import datetime

from database.funcs import Database

from discord import app_commands
from discord.ext import tasks, commands
from dotenv import load_dotenv

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz


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


    #Birthday checks
    scheduler = AsyncIOScheduler(timezone=pytz.timezone("Europe/Madrid"))
    @scheduler.scheduled_job(CronTrigger(hour=0, minute=0, day_of_week="mon"))
    async def scheduled_announce_week():
        await announce_upcoming_birthdays()

    @scheduler.scheduled_job(CronTrigger(hour=0, minute=0))
    async def scheduled_announce_today():
        await announce_today_birthdays()

    @bot.event
    async def on_ready():
        ...
        scheduler.start()


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
            print("User already have a birthday. Updating it...")
            await db.execute(
                "UPDATE birthdays SET bday_day = $1, bday_month = $2 WHERE discord_id = $3",
                day, month, user_id
            )
            message = f"🎂 Birthday updated successfully to {day}/{month}!"
        else:
            print("Adding new user birthday...")
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
    """Removes the birthday of the user if it exists."""
    print("Removing birthday...")
    user_id = str(interaction.user.id)

    try:
        existing = await db.fetchrow("SELECT * FROM birthdays WHERE discord_id = $1", user_id)

        if existing:
            await db.execute(
                "DELETE FROM birthdays WHERE discord_id = $1",
                user_id
            )
            message = "🎂 Your birthday has been removed!"
        else:
            message = "ℹ️ You don't have a registered birthday."

    except Exception as e:
        print(f"[ERROR] Failed to remove birthday: {e}")
        message = "❌ Something went wrong trying to remove your birthday."

    await interaction.response.send_message(message)


@bot.tree.command(name="birthday_week", description="Check if any user has a birthday this week.")
async def birthday_week(interaction: discord.Interaction):
    """
    Slash command that checks for upcoming birthdays this week (on demand).
    """
    today = datetime.date.today()
    start_week = today - datetime.timedelta(days=today.weekday())  # Monday
    end_week = start_week + datetime.timedelta(days=6)

    try:
        upcoming_birthdays = await db.fetch(
            """
            SELECT discord_id, bday_day, bday_month FROM birthdays
            WHERE (bday_month = $1 AND bday_day >= $2) 
            OR (bday_month = $3 AND bday_day <= $4)
            OR (bday_month > $5 AND bday_month < $6)
            """,
            start_week.month, start_week.day,
            end_week.month, end_week.day,
            start_week.month, end_week.month
        )

        if upcoming_birthdays:
            message = "🎉 **Birthdays this week!** 🎉\n"
            for user in upcoming_birthdays:
                message += f"🎂 <@{user['discord_id']}> - {user['bday_day']}/{user['bday_month']}\n"
        else:
            message = "ℹ️ No upcoming birthdays this week."

    except Exception as e:
        print(f"[ERROR] Failed to fetch weekly birthdays: {e}")
        message = "❌ An error occurred while checking birthdays."

    await interaction.response.send_message(message)



async def announce_today_birthdays():
    """
    Announces birthdays happening today.
    """
    print("[INFO] Checking today's birthdays...")
    today = datetime.date.today()

    try:
        birthdays_today = await db.fetch(
            "SELECT discord_id FROM birthdays WHERE bday_day = $1 AND bday_month = $2",
            today.day, today.month
        )

        if birthdays_today:
            channel = bot.get_channel(int(os.getenv("SERVER_UPDATES_CHANNEL_ID")))
            if channel:
                mentions = " ".join(f"<@{user['discord_id']}>" for user in birthdays_today)
                await channel.send(f"🎂 @here Happy Birthday {mentions}! 🎉 Have an amazing day! 🎈")
            else:
                print("[WARN] Birthday channel not found.")
        else:
            print("[INFO] No birthdays today.")

    except Exception as e:
        print(f"[ERROR] Failed to announce today's birthdays: {e}")


async def announce_upcoming_birthdays():
    """
    Announces the birthdays for the upcoming week.
    """
    print("[INFO] Checking upcoming birthdays...")
    today = datetime.date.today()
    start_week = today - datetime.timedelta(days=today.weekday())  # Monday
    end_week = start_week + datetime.timedelta(days=6)

    try:
        upcoming_birthdays = await db.fetch(
            """
            SELECT discord_id, bday_day, bday_month FROM birthdays
            WHERE (bday_month = $1 AND bday_day >= $2) 
            OR (bday_month = $3 AND bday_day <= $4)
            OR (bday_month > $5 AND bday_month < $6)
            """,
            start_week.month, start_week.day,
            end_week.month, end_week.day,
            start_week.month, end_week.month
        )

        if upcoming_birthdays:
            channel = bot.get_channel(int(os.getenv("SERVER_UPDATES_CHANNEL_ID")))
            if channel:
                message = "📅 **Upcoming Birthdays this Week!** 🎉\n"
                for user in upcoming_birthdays:
                    message += f"🎂 <@{user['discord_id']}> - {user['bday_day']}/{user['bday_month']}\n"
                await channel.send(message)
            else:
                print("[WARN] Birthday channel not found.")
        else:
            print("[INFO] No upcoming birthdays this week.")

    except Exception as e:
        print(f"[ERROR] Failed to announce weekly birthdays: {e}")



# Run the bot
bot.run(os.getenv('DISCORD_TOKEN'))