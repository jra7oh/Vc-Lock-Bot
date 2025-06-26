import os
import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask
from threading import Thread

# Flask keep-alive
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run_webserver():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run_webserver)
    t.start()

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.voice_states = True  # needed for voice channel info

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

GUILD_ID = 1386044830290804938  # Your server ID as int

@tree.command(name="lockvc", description="Lock the current voice channel", guild=discord.Object(id=GUILD_ID))
async def lockvc(interaction: discord.Interaction):
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("You are not connected to a voice channel.", ephemeral=True)
        return

    vc = interaction.user.voice.channel

    failed_roles = []
    for role in interaction.guild.roles:
        if role.permissions.administrator:
            continue
        try:
            await vc.set_permissions(role, connect=False)
        except discord.Forbidden:
            failed_roles.append(role.name)

    if failed_roles:
        await interaction.response.send_message(
            f"🔒 Locked the voice channel **{vc.name}**, but failed to set permissions for roles: {', '.join(failed_roles)}",
            ephemeral=True
        )
    else:
        await interaction.response.send_message(f"🔒 Locked the voice channel **{vc.name}**! Only admins can join now.")

@tree.command(name="unlockvc", description="Unlock the current voice channel", guild=discord.Object(id=GUILD_ID))
async def unlockvc(interaction: discord.Interaction):
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("You are not connected to a voice channel.", ephemeral=True)
        return

    vc = interaction.user.voice.channel

    failed_roles = []
    for role in interaction.guild.roles:
        try:
            await vc.set_permissions(role, overwrite=None)
        except discord.Forbidden:
            failed_roles.append(role.name)

    if failed_roles:
        await interaction.response.send_message(
            f"🔓 Unlocked the voice channel **{vc.name}**, but failed to clear permissions for roles: {', '.join(failed_roles)}",
            ephemeral=True
        )
    else:
        await interaction.response.send_message(f"🔓 Unlocked the voice channel **{vc.name}**! Everyone can join now.")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")

    guild = bot.get_guild(GUILD_ID)
    if guild is None:
        try:
            guild = await bot.fetch_guild(GUILD_ID)
        except Exception as e:
            print(f"Failed to fetch guild: {e}")
            guild = None

    if guild is not None:
        try:
            await tree.clear_commands(guild=guild)
            print("Cleared all commands from guild.")

            await tree.sync(guild=guild)
            print("Synced fresh commands.")
        except Exception as e:
            print(f"Error syncing commands: {e}")
    else:
        print("Guild not found, skipping command sync.")

if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN")
    if not TOKEN:
        print("ERROR: DISCORD_TOKEN environment variable not set.")
        exit(1)

    keep_alive()
    bot.run(TOKEN)
