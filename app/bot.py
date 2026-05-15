import os
import logging
import time
import datetime
import discord

from discord import app_commands
from discord.ext import tasks, commands
from dotenv import load_dotenv

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

load_dotenv()
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_LOG_DIR = os.getenv("LOG_DIR", "/opt/discord-bot/logs")
LOG_DIR = os.path.abspath(DEFAULT_LOG_DIR)
LOG_FILE_PATH = os.getenv("ERROR_LOG_PATH", os.path.join(LOG_DIR, "errors.log"))

try:
    os.makedirs(LOG_DIR, exist_ok=True)
except PermissionError:
    local_log_dir = os.path.join(BASE_DIR, "logs")
    try:
        os.makedirs(local_log_dir, exist_ok=True)
        LOG_DIR = local_log_dir
        LOG_FILE_PATH = os.getenv("ERROR_LOG_PATH", os.path.join(LOG_DIR, "errors.log"))
        print(f"WARNING: Cannot write to {DEFAULT_LOG_DIR}. Falling back to local log directory {LOG_DIR}.")
    except Exception as fallback_error:
        print(f"ERROR: Cannot create fallback log directory {local_log_dir}: {fallback_error}")
        raise

logger = logging.getLogger("disc_bot")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

file_handler = logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)
logger.info("Logger initialized, writing errors to %s", LOG_FILE_PATH)

from database.funcs import Database

async def get_birthdays(user_id: str = None):
    """
    Fetches birthdays from the database. If user_id is None, fetches all.
    """
    if user_id:
        result = await db.fetch(
            "SELECT discord_id, bday_day, bday_month FROM birthdays WHERE discord_id = $1",
            user_id
        )
    else:
        result = await db.fetch(
            "SELECT discord_id, bday_day, bday_month FROM birthdays"
        )
    return result

async def get_username_from_id(bot, user_id: str):
    """
    Fetches the username from a user ID.
    If the user is not found, returns "ID:{user_id}".
    """
    try:
        user = await bot.fetch_user(int(user_id))
        return user.name if user else f"ID:{user_id}"
    except Exception:
        return f"ID:{user_id}"

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
    logger.info("%s ready to serve!", bot.user)
    await bot.change_presence(activity=discord.Game(name="Kweh!"))
    server_updates = bot.get_channel(int(os.getenv("SERVER_UPDATES_CHANNEL_ID")))

    #if server_updates:
        #await server_updates.send("**¡Kweh! I'm ready to serve!**")

    try:
        # Sync the commands
        await bot.tree.sync()
        logger.info("Commands synchronized.")
    except Exception as e:
        logger.error("Error on syncing commands: %s", e, exc_info=True)


    #Birthday checks
    scheduler = AsyncIOScheduler(timezone=pytz.timezone("Europe/Madrid"))
    @scheduler.scheduled_job(CronTrigger(hour=9, minute=0))
    async def scheduled_announce_week():
        await announce_upcoming_birthdays()

    @scheduler.scheduled_job(CronTrigger(hour=9, minute=0))
    async def scheduled_announce_today():
        await announce_today_birthdays()

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
    logger.info("Pinging...")
    start_time = time.perf_counter()
    
    await interaction.response.send_message("Pong!")

    end_time = time.perf_counter()
    elapsed_time = (end_time - start_time) * 1000 # in milliseconds

    logger.info("Latency: %.2fms", elapsed_time)


## Birthdays
@bot.tree.command(name="birthday_add", description="Register a birthday.")
async def birthday_add(interaction: discord.Interaction, day: int, month: int):
    """Register a birthday if the user doesn't have one. If it does, it updates the stored date."""
    logger.info("Registering birthday for user %s", interaction.user.id)
    user_id = str(interaction.user.id)

    await interaction.response.defer(ephemeral=False)

    try:
        existing = await db.fetchrow("SELECT * FROM birthdays WHERE discord_id = $1", user_id)

        if existing:
            existing_day = existing[1]
            existing_month = existing[2]
            if existing_day == day and existing_month == month:
                logger.info("User %s submitted the same birthday %s/%s.", user_id, day, month)
                message = f"🎂 Your birthday is already registered as {day}/{month}."
            else:
                logger.info("User %s already has a birthday. Updating it from %s/%s to %s/%s.", user_id, existing_day, existing_month, day, month)
                await db.execute(
                    "UPDATE birthdays SET bday_day = $1, bday_month = $2 WHERE discord_id = $3",
                    day, month, user_id
                )
                message = f"🎂 Birthday updated successfully to {day}/{month}!"
        else:
            logger.info("Adding new user birthday for %s", user_id)
            await db.execute(
                "INSERT INTO birthdays (discord_id, bday_day, bday_month) VALUES ($1, $2, $3)",
                user_id, day, month
            )
            message = f"🎉 Birthday registered successfully on {day}/{month}!"

    except Exception as e:
        logger.error("An error occurred while saving birthday for %s: %s", user_id, e, exc_info=True)
        message = "❌ An error occurred while saving your birthday."

    await interaction.followup.send(message)


@bot.tree.command(name="birthday_remove", description="Remove a birthday.")
async def birthday_remove(interaction: discord.Interaction):
    """Removes the birthday of the user if it exists."""
    logger.info("Removing birthday for user %s", interaction.user.id)
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
        logger.error("Failed to remove birthday for %s: %s", user_id, e, exc_info=True)
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
        logger.error("Failed to fetch weekly birthdays: %s", e, exc_info=True)
        message = "❌ An error occurred while checking birthdays."

    await interaction.response.send_message(message)

@bot.tree.command(name="birthday_check_all", description="List all registered birthdays.")
async def birthday_check_all(interaction: discord.Interaction):
    """
    Lists all registered birthdays in the database.
    """
    try:
        birthdays = await get_birthdays()
        if birthdays:
            message = "🎂 **Registered Birthdays:**\n"
            for user in birthdays:
                username = await get_username_from_id(bot, user['discord_id'])
                message += f"{username} - {user['bday_day']}/{user['bday_month']}\n"
        else:
            message = "ℹ️ No birthdays registered."
    except Exception as e:
        logger.error("Failed to fetch all birthdays: %s", e, exc_info=True)
        message = "❌ An error occurred while fetching all birthdays."
    await interaction.response.send_message(message)


@bot.tree.command(name="birthday_check", description="Check a user's birthday by username.")
@app_commands.describe(username="Discord username to check birthday for.")
async def birthday_check(interaction: discord.Interaction, username: str):
    """
    Checks a user's birthday by their Discord username.
    """
    try:
        # Fetch all birthdays and compare names
        birthdays = await get_birthdays()
        found = None
        for user in birthdays:
            uname = await get_username_from_id(bot, user['discord_id'])
            if uname.lower() == username.lower():
                found = user
                break
        if found:
            message = f"🎂 {username} birthday is {found['bday_day']}/{found['bday_month']}"
        else:
            message = "ℹ️ No birthday registered for that username."
    except Exception as e:
        logger.error("Failed to fetch birthday for %s: %s", username, e, exc_info=True)
        message = "❌ An error occurred while fetching the birthday."
    await interaction.response.send_message(message)


async def announce_today_birthdays():
    """
    Announces birthdays happening today.
    """
    logger.info("Checking today's birthdays...")
    today = datetime.date.today()

    try:
        birthdays_today = await db.fetch(
            "SELECT discord_id FROM birthdays WHERE bday_day = $1 AND bday_month = $2",
            today.day, today.month
        )

        if birthdays_today:
            channel = bot.get_channel(int(os.getenv("SERVER_UPDATES_CHANNEL_ID")))
            if channel:
                for user in birthdays_today:
                    await channel.send(f"Kweh! Kweh! @everyone felicitad a <@{user['discord_id']}> 🎉🥳")
            else:
                logger.warning("Birthday channel not found.")
        else:
            logger.info("No birthdays today.")

    except Exception as e:
        logger.error("Failed to announce today's birthdays: %s", e, exc_info=True)


@bot.tree.command(name="birthday_announce_today", description="Announce today's birthdays manually.")
async def birthday_announce_today(interaction: discord.Interaction):
    try:
        await announce_today_birthdays()
        await interaction.response.send_message("✅ Today's birthday announcement triggered.", ephemeral=True)
    except Exception as e:
        logger.error("Failed to trigger today's birthdays: %s", e, exc_info=True)
        await interaction.response.send_message("❌ Failed to trigger today's birthday announcement.", ephemeral=True)


async def announce_upcoming_birthdays():
    """
    Announces the birthdays for the next 7 days.
    """
    logger.info("Checking upcoming birthdays...")
    today = datetime.date.today()
    upcoming_birthdays = {}

    try:
        for delta in range(1, 8):
            check_date = today + datetime.timedelta(days=delta)
            birthdays = await db.fetch(
                "SELECT discord_id, bday_day, bday_month FROM birthdays WHERE bday_day = $1 AND bday_month = $2",
                check_date.day, check_date.month
            )
            for user in birthdays:
                if user['discord_id'] not in upcoming_birthdays:
                    upcoming_birthdays[user['discord_id']] = {
                        'discord_id': user['discord_id'],
                        'bday_day': user['bday_day'],
                        'bday_month': user['bday_month'],
                        'check_date': check_date
                    }

        if upcoming_birthdays:
            channel = bot.get_channel(int(os.getenv("SERVER_UPDATES_CHANNEL_ID")))
            if channel:
                for user in upcoming_birthdays.values():
                    username = await get_username_from_id(bot, user['discord_id'])
                    birthday_text = f"{user['bday_day']}/{user['bday_month']}"
                    await channel.send(
                        f"Kweh! Cumpleaños a la vista 👀 de **{username}** el {birthday_text}"
                    )
            else:
                logger.warning("Birthday channel not found.")
        else:
            logger.info("No upcoming birthdays in the next 7 days.")

    except Exception as e:
        logger.error("Failed to announce upcoming birthdays: %s", e, exc_info=True)


@bot.tree.command(name="birthday_announce_upcoming", description="Announce upcoming birthdays in the next 7 days.")
async def birthday_announce_upcoming(interaction: discord.Interaction):
    try:
        await announce_upcoming_birthdays()
        await interaction.response.send_message("✅ Upcoming birthday announcement triggered.", ephemeral=True)
    except Exception as e:
        logger.error("Failed to trigger upcoming birthdays: %s", e, exc_info=True)
        await interaction.response.send_message("❌ Failed to trigger upcoming birthday announcement.", ephemeral=True)


# Run the bot
bot.run(os.getenv('DISCORD_TOKEN'))
