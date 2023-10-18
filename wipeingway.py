import os
import asyncio
import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta

#discord stuff
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True

#set up prefix
bot = commands.Bot(command_prefix='!', intents=intents)

#importing environment variables
#TOKEN = os.environ["DISCORD_TOKEN"]

#test if bot is ready
@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

@bot.command()
async def schedule_message(ctx, time_str, channel_name, *, message):
    time = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
    current_time = datetime.now()
    time_diff = (time - current_time).total_seconds()

    if time_diff <= 0:
        await ctx.send("Invalid time. The specified time must be in the future.")
        return

    channel = discord.utils.get(ctx.guild.channels, name=channel_name)
    if not channel:
        await ctx.send("Invalid channel name. Please provide a valid channel name.")
        return

    await ctx.send(f"Scheduling a message in {channel.mention} at {time_str}.")
    await asyncio.sleep(time_diff)
    await channel.send(f"Message scheduled by {ctx.author.mention}: {message}")

@bot.command()
async def create_reminder(ctx, days_str, time_str, channel_name, *, message):
    days = days_str.split(',')
    time = datetime.strptime(time_str, '%H:%M')
    current_time = datetime.now()
    target_day = None

    # Find the next occurrence of the specified day
    for day in days:
        day = day.lower().strip()
        target_day = current_time + timedelta(days=(7 - current_time.weekday() + days.index(day)) % 7)
        if target_day.date() > current_time.date():
            break

    target_time = datetime(
        year=target_day.year,
        month=target_day.month,
        day=target_day.day,
        hour=time.hour,
        minute=time.minute
    )

    time_diff = (target_time - current_time).total_seconds()

    if time_diff <= 0:
        await ctx.send("Invalid time. The specified time must be in the future.")
        return

    channel = discord.utils.get(ctx.guild.channels, name=channel_name)
    if not channel:
        await ctx.send("Invalid channel name. Please provide a valid channel name.")
        return

    await ctx.send(f"Creating a reminder in {channel.mention} on {', '.join(days)} at {time_str}.")

    async def send_reminder():
        while True:
            await asyncio.sleep(time_diff)
            await channel.send(f"Reminder in {channel.mention}: {message}")
            await asyncio.sleep(604800)  # Sleep for 7 days (604,800 seconds) for weekly reminders

    bot.loop.create_task(send_reminder())


#hello world message
@bot.event
async def on_ready():
    print(f'Bot connected as {bot.user.name}')

# Run the bot
TOKEN = "OTk3NzA5OTE5NTA1NjMzMzUw.GX571H.aAOB1qcUpcJ2CtWSRIVlj-wTXiu_M_rHkMDThU"
bot.run(TOKEN)