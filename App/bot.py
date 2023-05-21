import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!')
TOKEN = os.environ["WIPE_TOKEN"]

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

@bot.event
async def on_ready():
    print(f'Bot connected as {bot.user.name}')

# Run the bot
bot.run(TOKEN)
