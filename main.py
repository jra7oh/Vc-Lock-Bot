import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.voice_states = True

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

TOKEN = os.getenv("MTM4NzU1NTM1Mzg1MTQ2NTc5MA.GqEsfj.C3QknF-AVLKpY1kkX53tc-LIYpIti907-07YU4")
bot.run(TOKEN)
