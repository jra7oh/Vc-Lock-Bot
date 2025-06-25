import discord
from discord import app_commands
from discord.ext import commands
from flask import Flask
import threading
import os

TOKEN = "YOUR_BOT_TOKEN_HERE"  # Replace with your bot token
GUILD_ID = 1386044830290804938  # Your server ID (int)

intents = discord.Intents.default()
intents.message_content = False  # Not needed for slash commands

bot = commands.Bot(command_prefix="/", intents=intents)

# Flask app setup
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

# Lock VC command
@bot.tree.command(name="lockvc", description="Lock the current voice channel", guild=discord.Object(id=GUILD_ID))
async def lockvc(interaction: discord.Interaction):
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("You must be connected to a voice channel to use this command.", ephemeral=True)
        return

    channel = interaction.user.voice.channel

    overwrite = channel.overwrites_for(interaction.guild.default_role)
    if overwrite.connect is False:
        await interaction.response.send_message("The channel is already locked!", ephemeral=True)
        return

    try:
        overwrite.connect = False
        await channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
        await interaction.response.send_message(f"🔒 Locked the voice channel: **{channel.name}**")
    except discord.Forbidden:
        await interaction.response.send_message("I do not have permission to modify channel permissions.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)

# Unlock VC command
@bot.tree.command(name="unlockvc", description="Unlock the current voice channel", guild=discord.Object(id=GUILD_ID))
async def unlockvc(interaction: discord.Interaction):
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("You must be connected to a voice channel to use this command.", ephemeral=True)
        return

    channel = interaction.user.voice.channel

    overwrite = channel.overwrites_for(interaction.guild.default_role)
    if overwrite.connect is None or overwrite.connect is True:
        await interaction.response.send_message("The channel is already unlocked!", ephemeral=True)
        return

    try:
        overwrite.connect = None  # Reset permission to default (allow connect)
        await channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
        await interaction.response.send_message(f"🔓 Unlocked the voice channel: **{channel.name}**")
    except discord.Forbidden:
        await interaction.response.send_message("I do not have permission to modify channel permissions.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)

if __name__ == "__main__":
    # Start Flask app in a separate thread
    threading.Thread(target=run_flask).start()

    # Run Discord bot
    bot.run(TOKEN)
