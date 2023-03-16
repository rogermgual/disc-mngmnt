import discord
import interactions
import sys
from discord.ext import commands
from discord_slash import SlashCommand

print(sys.path)

sys.path.append('/home/hrodger/.local/lib/python3.9/site-packages')
print(sys.path)

TOKEN = os.environ["WIPE_TOKEN"]

bot = commands.Bot(command_prefix='/')
slash = SlashCommand(bot, sync_commands=True)

@slash.slash(name="ping")
async def _ping(ctx):
    await ctx.send("Pong!")

@slash.slash(name="server")
async def _server(ctx):
    guild = ctx.guild
    await ctx.send(f"Server name: {guild.name}\nTotal members: {guild.member_count}")

bot.run(TOKEN)
session.close()