from typing import Final

import os
import discord
from discord import Intents,Client,Message
from discord.ext import commands, tasks
from discord import app_commands
from dotenv import load_dotenv
from datetime import datetime, timedelta


from get_prayer_time import get_prayer_time
from get_quran_verse import get_quran_verse

#**Load TOKEN
load_dotenv()
TOKEN: Final[str]= os.getenv('DISCORD_TOKEN')

#BOT SETUP
intents: Intents = Intents.default()
intents.message_content= True
client : Client = Client(intents=intents)

bot = commands.Bot(command_prefix='/', intents=intents)





#Startup
@bot.event
async def on_ready() ->None:
    print(f'{bot.user}is now running!')
    await bot.tree.sync()
    #prayer_time_notification.start()                   #! Disabled for now ...
    send_quran.start()

#todo : i need to fix this , not working well ...

@tasks.loop(hours=3)  
async def prayer_time_notification():
    now = datetime.now().strftime('%H:%M')
    try:
        timings = get_prayer_time()
    except Exception as e:
        print(f"Failed to fetch prayer times: {e}")
        return

    channel = bot.get_channel(1337175557271715920) 

    if channel is None:
        print(f"The channel id {1337175557271715920} doesnt exist")
        return

    for prayer, time in timings.items():
        
        prayer_time = datetime.strptime(time, '%H:%M').strftime('%H:%M')

        if now == prayer_time:
            await channel.send(f"@everyone ({prayer})حان الأن موعد صلاة الـ ")
        
        if now == prayer_time and prayer == "Imsak":
            await channel.send(file=discord.File("/resources/zaki.mp4"))
        if prayer == "Maghrib":
            maghrib_time = datetime.strptime(time, '%H:%M')
            ten_minutes_after = (maghrib_time + timedelta(minutes=10)).strftime('%H:%M')
            if now == ten_minutes_after:
                await channel.send("تم تعبئة الكرشة بنجاح")
                await channel.send(file=discord.File("/resources/zaki.jpg"))



#Random Quran Verse

@tasks.loop(minutes=1) #todo: change to houres = 2 later , "mins" for test
async def send_quran():
    channel = bot.get_channel(1337175557271715920) 

    if channel is None:
        print(f"The channel ID {1337175557271715920} doesn't exist.")
        return

    
    quran_verse = get_quran_verse()
    await channel.send(f"**Quran Verse of the Hour:**\n{quran_verse}")

#ramadan command            
@bot.command(name="ramadan")
async def ramadan(ctx):
    await ctx.send("Ramadan Mubarak! May this blessed month bring you peace and prosperity.")

#remind command
@bot.command(name="remind",description="Remind you of futor or suhoor")
async def remind(ctx, meal: str, time: str):
    if meal.lower() == "suhoor":
        await ctx.send(f"Reminder set for Suhoor at {time}.")
    elif meal.lower() == "iftar":
        await ctx.send(f"Reminder set for Iftar at {time}.")
    else:
        await ctx.send("Please specify 'suhoor' or 'iftar'.")

@bot.hybrid_command(name="prayertime", with_app_command=True, description="Show prayer times for today")
async def prayertime(ctx):
    try:
        timings = get_prayer_time()
    except Exception as e:
        await ctx.send(f"Sorry,Failed to fetch prayer times: {e}")
        return
    embeded_message = discord.Embed(title="Prayer time", description=f"Here are the prayer times for {datetime.now().strftime('%d-%m-%Y')}")
    embeded_message.set_thumbnail(url=ctx.author.avatar)
    embeded_message.add_field(name="Fajr", value=timings["Fajr"])
    embeded_message.add_field(name="Sunrise", value=timings["Sunrise"])
    embeded_message.add_field(name="Dhuhr", value=timings["Dhuhr"])
    embeded_message.add_field(name="Asr", value=timings["Asr"])
    embeded_message.add_field(name="Maghrib", value=timings["Maghrib"])
    embeded_message.add_field(name="Isha", value=timings["Isha"])

    await ctx.send(embed=embeded_message)


#Main entry
def main() -> None:
    bot.run(token=TOKEN)

if __name__== '__main__':
    main()
