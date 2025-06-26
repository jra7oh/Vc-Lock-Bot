import os
import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask
from threading import Thread

# Flask web server for uptime pings
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run_webserver():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run_webserver)
    t.start()

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True  # Needed for role editing

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# Replace with your actual server ID
GUILD_ID = 1386044830290804938

# /lockvc command (now works even if user is not in VC)
@tree.command(name="lockvc", description="Lock a voice channel", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(channel="Select the voice channel to lock")
async def lockvc(interaction: discord.Interaction, channel: discord.VoiceChannel):
    await interaction.response.defer(thinking=True, ephemeral=True)

    failed_roles = []

    for role in interaction.guild.roles:
        if role.permissions.administrator:
            continue
        try:
            await channel.set_permissions(role, connect=False)
        except discord.Forbidden:
            failed_roles.append(role.name)

    if failed_roles:
        await interaction.followup.send(
            f"🔒 Locked **{channel.name}**, but couldn't lock for: `{', '.join(failed_roles)}`"
        )
    else:
        await interaction.followup.send(f"🔒 Locked **{channel.name}**! Only admins can join.")

# /unlockvc command
@tree.command(name="unlockvc", description="Unlock a voice channel", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(channel="Select the voice channel to unlock")
async def unlockvc(interaction: discord.Interaction, channel: discord.VoiceChannel):
    await interaction.response.defer(thinking=True, ephemeral=True)

    failed_roles = []

    for role in interaction.guild.roles:
        try:
            await channel.set_permissions(role, overwrite=None)
        except discord.Forbidden:
            failed_roles.append(role.name)

    if failed_roles:
        await interaction.followup.send(
            f"🔓 Unlocked **{channel.name}**, but couldn't reset for: `{', '.join(failed_roles)}`"
        )
    else:
        await interaction.followup.send(f"🔓 Unlocked **{channel.name}**! Everyone can join.")

# Bot ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")

    guild = discord.Object(id=GUILD_ID)
    tree.clear_commands(guild=guild)
    print("Cleared old commands...")

    await tree.sync(guild=guild)
    print("Synced new commands ✅")

# Start the bot
if __name__ == "__main__":
    keep_alive()
    TOKEN = os.getenv("DISCORD_TOKEN")
    if not TOKEN:
        print("❌ ERROR: DISCORD_TOKEN environment variable not set.")
        exit(1)
    bot.run(TOKEN)
