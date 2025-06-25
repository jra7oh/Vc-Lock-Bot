import os
import discord
from discord import app_commands
from discord.ext import commands

intents = discord.Intents.default()
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Your actual Discord server ID
GUILD_ID = 1386044830290804938
guild = discord.Object(id=GUILD_ID)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    await bot.tree.sync(guild=guild)
    print("Slash commands synced.")

@bot.tree.command(name="lockvc", description="Lock a voice channel", guild=guild)
@app_commands.describe(channel="The voice channel to lock")
async def lockvc(interaction: discord.Interaction, channel: discord.VoiceChannel):
    overwrite = channel.overwrites_for(interaction.guild.default_role)
    if overwrite.connect is False:
        await interaction.response.send_message(f"🔒 The channel **{channel.name}** is already locked!", ephemeral=True)
        return

    overwrite.connect = False
    await channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
    await interaction.response.send_message(f"🔒 Locked the voice channel **{channel.name}**!")

@bot.tree.command(name="unlockvc", description="Unlock a voice channel", guild=guild)
@app_commands.describe(channel="The voice channel to unlock")
async def unlockvc(interaction: discord.Interaction, channel: discord.VoiceChannel):
    overwrite = channel.overwrites_for(interaction.guild.default_role)
    if overwrite.connect is True or overwrite.connect is None:
        await interaction.response.send_message(f"🔓 The channel **{channel.name}** is already unlocked!", ephemeral=True)
        return

    overwrite.connect = True
    await channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
    await interaction.response.send_message(f"🔓 Unlocked the voice channel **{channel.name}**!")

# Run the bot with token from environment variable
bot.run(os.getenv("DISCORD_TOKEN"))
