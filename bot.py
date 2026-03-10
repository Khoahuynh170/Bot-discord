import discord
from discord.ext import commands
import yt_dlp
import asyncio

TOKEN = "YOUR_TOKEN"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="k!", intents=intents)

queue = []

ydl_opts = {
    'format': 'bestaudio',
    'noplaylist': True
}

@bot.event
async def on_ready():
    print("Bot ready")

async def play_next(ctx):
    if len(queue) > 0:
        url = queue.pop(0)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info['url']
            title = info['title']

        source = await discord.FFmpegOpusAudio.from_probe(audio_url)

        ctx.voice_client.play(
            source,
            after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop)
        )

        await ctx.send(f"🎵 Đang phát: {title}")

@bot.command()
async def join(ctx):
    if ctx.author.voice is None:
        await ctx.send("Bạn phải vào voice channel")
        return

    channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        await channel.connect()

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

@bot.command()
async def play(ctx, *, search):

    if ctx.voice_client is None:
        await ctx.invoke(join)

    if not search.startswith("http"):
        search = f"ytsearch:{search}"

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(search, download=False)

        if "entries" in info:
            info = info["entries"][0]

        url = info["webpage_url"]
        title = info["title"]

    queue.append(url)

    await ctx.send(f"Đã thêm vào queue: {title}")

    if not ctx.voice_client.is_playing():
        await play_next(ctx)

@bot.command()
async def skip(ctx):
    ctx.voice_client.stop()

@bot.command()
async def pause(ctx):
    ctx.voice_client.pause()

@bot.command()
async def resume(ctx):
    ctx.voice_client.resume()

@bot.command()
async def stop(ctx):
    queue.clear()
    ctx.voice_client.stop()

bot.run(TOKEN)
