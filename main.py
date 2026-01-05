import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Bot {bot.user.name} Online di Koyeb!')

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        await ctx.author.voice.channel.connect()
        await ctx.send(f"✅ Bot masuk ke {ctx.author.voice.channel.name}")
    else:
        await ctx.send("Masuk ke voice dulu!")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Keluar.")

token = os.getenv('DISCORD_TOKEN')
bot.run(token)