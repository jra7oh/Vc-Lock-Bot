import discord
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

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def lockvc(ctx):
    if ctx.author.voice:
        vc = ctx.author.voice.channel
        await vc.set_permissions(ctx.guild.default_role, connect=False)
        await ctx.send(f"🔒 Locked **{vc.name}**")
    else:
        await ctx.send("⚠️ You're not in a voice channel.")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlockvc(ctx):
    if ctx.author.voice:
        vc = ctx.author.voice.channel
        await vc.set_permissions(ctx.guild.default_role, connect=True)
        await ctx.send(f"🔓 Unlocked **{vc.name}**")
    else:
        await ctx.send("⚠️ You're not in a voice channel.")

keep_alive()
TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
