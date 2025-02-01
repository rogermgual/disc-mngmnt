import os
import discord
from discord import app_commands
from discord.ext import tasks, commands
from dotenv import load_dotenv
from database.db import Database

# Cargamos las variables de entorno
load_dotenv()

# Configuramos el bot
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Conexión a la base de datos
db = Database()

@bot.event
async def on_ready():
    print(f'Bot {bot.user} está listo!')
    await bot.change_presence(activity=discord.Game(name="Organizando eventos"))
    check_birthdays.start()

@tasks.loop(hours=24)
async def check_birthdays():
    # Aquí irá la lógica para revisar los cumpleaños
    pass

@bot.tree.command(name="recordar_cumpleaños", description="Registra tu cumpleaños")
async def recordar_cumpleaños(interaction: discord.Interaction, fecha: str):
    # Lógica para registrar el cumpleaños
    await interaction.response.send_message(f"Cumpleaños registrado: {fecha}")

@bot.tree.command(name="recordatorio", description="Crea un recordatorio")
async def recordatorio(interaction: discord.Interaction, mensaje: str, fecha: str, canal: discord.TextChannel, periodicidad: int):
    # Lógica para crear un recordatorio
    await interaction.response.send_message(f"Recordatorio creado: {mensaje}")

@bot.tree.command(name="evento_raid", description="Organiza un evento de raid")
async def evento_raid(interaction: discord.Interaction, evento: str, contenido: str, fecha: str):
    # Lógica para crear un evento de raid
    await interaction.response.send_message(f"Evento de raid creado: {evento}")

# Iniciamos el bot
bot.run(os.getenv('DISCORD_TOKEN'))