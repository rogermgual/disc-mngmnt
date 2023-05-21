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
TOKEN = os.environ["WIPE_TOKEN"]

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


#hello world message
@bot.event
async def on_ready():
    print(f'Bot connected as {bot.user.name}')

# Run the bot
bot.run(TOKEN)