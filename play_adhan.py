import discord
import asyncio

async def play_adhan(guild: discord.Guild):
    adhan_url = "https://www.islamcan.com/audio/adhan/azan1.mp3"
    voice_channel = None
    
    
    for channel in guild.voice_channels:
        if len(channel.members) > 0 and channel.permissions_for(guild.me).connect:
            voice_channel = channel
            break

    if voice_channel is None:
        print(f"❌ no Active members in VC or no channel found on {guild.name}")
        return

    vc = await voice_channel.connect()
    
    try:
        audio_source = discord.FFmpegPCMAudio(adhan_url)
        vc.play(audio_source)
        print("🎵 Streaming Adhan...")

        while vc.is_playing():
            await asyncio.sleep(1)

    except Exception as e:
        print(f"❌ Error streaming Adhan: {e}")

    print("✅ Adhan finished, disconnecting...")
    await vc.disconnect()