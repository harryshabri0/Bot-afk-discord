import discord
from discord.ext import commands
import os
import http.server
import socketserver
import threading
import asyncio
import yt_dlp

# --- KONFIGURASI AUDIO ---
yt_dlp.utils.bug_reports_message = lambda: ''
ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}
ffmpeg_options = {
    'options': '-vn',
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            data = data['entries'][0]
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

# --- PENIPU PORT UNTUK KOYEB ---
def run_dummy_server():
    PORT = 8080
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Web Server berjalan di port {PORT}")
        httpd.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# --- KODE BOT DISCORD ---
intents = discord.Intents.default()
intents.message_content = True 

# MENGUBAH PREFIX MENJADI "Harry tolong "
# case_insensitive=True agar "harry tolong" (huruf kecil) juga bisa
bot = commands.Bot(command_prefix=['Harry tolong ', 'harry tolong '], intents=intents, case_insensitive=True)

loop_status = {}

@bot.event
async def on_ready():
    print(f'✅ Bot {bot.user.name} Online! Gunakan perintah: Harry tolong mainkan [link]')

@bot.command()
async def join(ctx):
    if not ctx.author.voice:
        return await ctx.send("❌ Kamu harus masuk ke voice channel dulu!")
    channel = ctx.author.voice.channel
    if ctx.voice_client is not None:
        return await ctx.voice_client.move_to(channel)
    await channel.connect()
    await ctx.send(f"✅ Harry sudah masuk ke {channel.name}")

# PERINTAH DIUBAH MENJADI 'mainkan'
@bot.command()
async def mainkan(ctx, *, url):
    """Memutar lagu dari URL atau pencarian judul"""
    async with ctx.typing():
        if not ctx.voice_client:
            await ctx.invoke(join)

        player = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
        
        def after_playing(error):
            if error:
                print(f'Player error: {error}')
            # Logika Looping
            if loop_status.get(ctx.guild.id):
                coro = play_logic(ctx, url)
                asyncio.run_coroutine_threadsafe(coro, bot.loop)

        ctx.voice_client.play(player, after=after_playing)
    
    await ctx.send(f'🎶 Harry sedang memutar: **{player.title}**')

async def play_logic(ctx, url):
    """Helper untuk fungsi loop"""
    player = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
    def after_playing(error):
        if loop_status.get(ctx.guild.id):
            asyncio.run_coroutine_threadsafe(play_logic(ctx, url), bot.loop)
    if ctx.voice_client:
        ctx.voice_client.play(player, after=after_playing)

@bot.command()
async def loop(ctx):
    """Mengaktifkan/Matikan loop lagu"""
    guild_id = ctx.guild.id
    status = loop_status.get(guild_id, False)
    loop_status[guild_id] = not status
    
    label = "Aktif" if loop_status[guild_id] else "Mati"
    await ctx.send(f"🔄 Looping sekarang: **{label}**")

@bot.command()
async def leave(ctx):
    """Keluar dari voice channel"""
    if ctx.voice_client:
        loop_status[ctx.guild.id] = False 
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Harry pamit keluar.")
    else:
        await ctx.send("Harry tidak ada di voice channel.")

@bot.command()
async def stop(ctx):
    """Berhenti memutar lagu"""
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.send("⏹️ Musik dihentikan oleh Harry.")

token = os.getenv('DISCORD_TOKEN')
bot.run(token)
