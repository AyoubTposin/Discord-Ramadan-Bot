import discord
import asyncio

async def play_adhan(guild: discord.Guild):
    file_path = "resources/adhan.opus"
    voice_channel = None
    
    
    # **Find a voice channel with active members**
    for channel in guild.voice_channels:
        if len(channel.members) > 0 and channel.permissions_for(guild.me).connect:
            voice_channel = channel
            break

    if voice_channel is None:
        print(f"❌ no Active members in VC or no channel found on {guild.name}")
        return

    vc = await voice_channel.connect()
    
    if not discord.opus.is_loaded():
        discord.opus.load_opus("libopus.so")
    
    audio_source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(file_path))
    
    if vc.is_playing():
        vc.stop()
        
    vc.play(audio_source)
    print("Adhan is playing ...")

    while vc.is_playing():
        await asyncio.sleep(1)
        
    await vc.disconnect()
    print("✅ Adhan finished, bot disconnected.")