import discord
from discord.ext import commands
import yt_dlp
import asyncio

import os
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="k!", intents=intents)

queue = []

ytdl_format_options = {
    'format': 'bestaudio/best',
    'quiet': True
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

async def play_next(ctx):
    if len(queue) > 0:
        url = queue.pop(0)
        await play_music(ctx, url)

async def play_music(ctx, url):

    voice = ctx.voice_client

    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

    song_url = data['url']

    source = discord.FFmpegPCMAudio(song_url, executable="ffmpeg", **ffmpeg_options)

    voice.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop))

@bot.event
async def on_ready():
    print("Bot ready")

@bot.command()
async def join(ctx):

    if ctx.author.voice is None:
        await ctx.send("Bạn chưa vào voice")
        return

    channel = ctx.author.voice.channel
    await channel.connect()

@bot.command()
async def leave(ctx):

    if ctx.voice_client:
        await ctx.voice_client.disconnect()

@bot.command()
async def play(ctx, *, url):

    if ctx.voice_client is None:
        await ctx.invoke(join)

    if ctx.voice_client.is_playing():
        queue.append(url)
        await ctx.send("Đã thêm vào queue")
    else:
        await play_music(ctx, url)

@bot.command()
async def skip(ctx):

    if ctx.voice_client:
        ctx.voice_client.stop()

@bot.command()
async def queue_list(ctx):

    if len(queue) == 0:
        await ctx.send("Queue trống")
    else:
        msg = "\n".join(queue)
        await ctx.send(msg)
@bot.command()
async def ping(ctx):
    await ctx.send("pong")
bot.run(TOKEN)
