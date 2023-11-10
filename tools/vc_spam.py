import discord
import asyncio

def vc_spam(token, file, voice_id):
    client = discord.Client(status=discord.Status.offline)
    
    @client.event
    async def on_ready():
        await asyncio.sleep(2)
        voice_channel = client.get_channel(voice_id)
        while not client.is_closed():
            vc = await voice_channel.connect()
            vc.play(discord.FFmpegPCMAudio(file))
            vc.source = discord.PCMVolumeTransformer(vc.source)
            vc.source.volume = 10.0
            while vc.is_playing():
                await asyncio.sleep(0.5)
            try:
                client.logout()
            except:
                pass
            await vc.disconnect(force=True)
            return
            
    try:
        client.run(token, bot=False)
    except:
        pass
            
        
            
        
    