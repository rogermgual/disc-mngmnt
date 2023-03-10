import os
import discord

TOKEN = os.environ["WIPE_TOKEN"]

intents = discord.Intents.default()
client = discord.Client(intents)

@client.event
async def on_ready():
    print('Bot en línea')

@client.event
async def on_message(message):
    if message.content.startswith('!hola'):
        await message.channel.send('¡Hola!')

client.run(TOKEN)
