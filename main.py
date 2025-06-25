import discord
from discord import app_commands
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)

@tree.command(name="lockvc", description="Lock a voice channel")
@app_commands.describe(channel="Select the voice channel to lock")
@commands.has_permissions(manage_channels=True)
async def lockvc(interaction: discord.Interaction, channel: discord.VoiceChannel):
    await channel.set_permissions(interaction.guild.default_role, connect=False)
    await interaction.response.send_message(f"🔒 Locked **{channel.name}**", ephemeral=True)

@tree.command(name="unlockvc", description="Unlock a voice channel")
@app_commands.describe(channel="Select the voice channel to unlock")
@commands.has_permissions(manage_channels=True)
async def unlockvc(interaction: discord.Interaction, channel: discord.VoiceChannel):
    await channel.set_permissions(interaction.guild.default_role, overwrite=None)
    await interaction.response.send_message(f"🔓 Unlocked **{channel.name}**", ephemeral=True)

keep_alive()
TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
