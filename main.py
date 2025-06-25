import os
import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask
from threading import Thread

# ----- Flask app to keep Render service alive -----
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run_webserver():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run_webserver)
    t.start()

# ----- Discord Bot setup -----
intents = discord.Intents.default()
intents.message_content = True  # if you need message content
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

GUILD_ID = 1386044830290804938  # Your server ID as int

# ----- Commands -----
@tree.command(name="lockvc", description="Lock the current voice channel", guild=discord.Object(id=GUILD_ID))
async def lockvc(interaction: discord.Interaction):
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("You are not connected to a voice channel.", ephemeral=True)
        return
    
    vc = interaction.user.voice.channel
    overwrite = vc.overwrites_for(interaction.guild.default_role)

    if overwrite.connect is False:
        await interaction.response.send_message("The channel is already locked!", ephemeral=True)
        return

    overwrite.connect = False
    try:
        await vc.set_permissions(interaction.guild.default_role, overwrite=overwrite)
        await interaction.response.send_message(f"🔒 Locked the voice channel **{vc.name}**!")
    except discord.Forbidden:
        await interaction.response.send_message("I don't have permission to manage channel permissions.", ephemeral=True)

@tree.command(name="unlockvc", description="Unlock the current voice channel", guild=discord.Object(id=GUILD_ID))
async def unlockvc(interaction: discord.Interaction):
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("You are not connected to a voice channel.", ephemeral=True)
        return
    
    vc = interaction.user.voice.channel
    overwrite = vc.overwrites_for(interaction.guild.default_role)

    if overwrite.connect is None or overwrite.connect is True:
        await interaction.response.send_message("The channel is already unlocked!", ephemeral=True)
        return

    overwrite.connect = None  # Remove the overwrite to unlock
    try:
        await vc.set_permissions(interaction.guild.default_role, overwrite=overwrite)
        await interaction.response.send_message(f"🔓 Unlocked the voice channel **{vc.name}**!")
    except discord.Forbidden:
        await interaction.response.send_message("I don't have permission to manage channel permissions.", ephemeral=True)

# ----- Bot events -----
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")
    # Sync commands to your guild (only do this once)
    try:
        await tree.sync(guild=discord.Object(id=GUILD_ID))
        print("Slash commands synced.")
    except Exception as e:
        print(f"Error syncing commands: {e}")

# ----- Main entry point -----
if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN")
    if not TOKEN:
        print("ERROR: DISCORD_TOKEN environment variable not set.")
        exit(1)
    
    keep_alive()
    bot.run(TOKEN)
