import discord
from discord.ext import commands
import os
import http.server
import socketserver
import threading

# --- PENIPU PORT UNTUK KOYEB ---
def run_dummy_server():
    # Membuat server web sederhana agar Koyeb menganggap aplikasi sehat
    PORT = 8080
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Web Server berjalan di port {PORT}")
        httpd.serve_forever()

# Jalankan server web di thread terpisah agar tidak mengganggu bot
threading.Thread(target=run_dummy_server, daemon=True).start()

# --- KODE BOT DISCORD ---
intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Bot {bot.user.name} Online di Koyeb Web Service!')

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

# Ambil token dari Environment Variable
token = os.getenv('DISCORD_TOKEN')
bot.run(token)
