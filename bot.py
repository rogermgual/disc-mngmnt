import discord

TOKEN = 'OTk3NzA5OTE5NTA1NjMzMzUw.Grznmk.AVq3w0MnZAqMULb5xL45YcE_oY12GGelLmYY2c'

client = discord.Client()

@client.event
async def on_ready():
    print('Bot en línea')

@client.event
async def on_message(message):
    if message.content.startswith('!hola'):
        await message.channel.send('¡Hola!')

client.run(TOKEN)
