from typing import Final

import settings
import discord
from discord import Intents,Client,Message
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime, timedelta


from get_prayer_time import get_prayer_time
from get_quran_verse import get_quran_verse




#BOT SETUP
logger= settings.logging.getLogger("bot")

intents: Intents = Intents.default()
intents.message_content= True


bot = commands.Bot(command_prefix='/', intents=intents)





#Startup
@bot.event
async def on_ready() ->None:
    print(f'{bot.user} is now running!')
    await bot.tree.sync()
    prayer_time_notification.start()                   #*Activated : still checking tho ...
    send_quran.start()
    
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Command not found!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❗ Missing argument!")
    else:
        await ctx.send("⚠️ An error occurred!")
        print(f"Error: {error}")  # Logs for debugging


@bot.command(
    aliases=['p'],
    help="this is help",                       #Probably should add real "Help" prompts as well
    description="this is description",
    brief="this is a ping command !"
)
async def ping(ctx):
    await ctx.send("pong")

#todo : Keep underwatch , might fail 

@tasks.loop(minutes=1)  
async def prayer_time_notification():
    now= datetime.now().time()
    try:
        timings = get_prayer_time()
    except Exception as e:
        print(f"Failed to fetch prayer times: {e}")
        return

    channel = bot.get_channel(1344067206346182668) 

    if isinstance(channel, discord.TextChannel):

        for prayer, time in timings.items():
            try:
                prayer_time = datetime.strptime(time, '%H:%M').time()  # Convert to time object
            except ValueError:
                print(f"Invalid time format for {prayer}: {time}")
                continue
    
            if now.hour == prayer_time.hour and now.minute == prayer_time.minute:
                await channel.send(f"@everyone ({prayer})حان الأن موعد صلاة الـ ")
            
            if prayer == "Imsak":
                await channel.send(file=discord.File("resources/zaki.mp4")) #* about that ... might consider it later
                
            if prayer == "Maghrib":
                maghrib_time = datetime.strptime(time, '%H:%M')
                ten_minutes_after = (maghrib_time + timedelta(minutes=10)).time()
                
                if now.hour == ten_minutes_after.hour and now.minute == ten_minutes_after.minute:
                        await channel.send("تم تعبئة الكرشة بنجاح")                       
                        await channel.send(file=discord.File("resources/zaki.jpg"))                #*Should add 30 diff pics , Each pic for each day , maybe ...
    else:
        print(f"❌ Error: Channel {channel} is not a TextChannel!")



#*Random Quran Verse

@tasks.loop(hours=4) #todo Currently 4 hours , might change 
async def send_quran():
    channel = bot.get_channel(1344067206346182668) 

    if isinstance(channel, discord.TextChannel):
        quran_verse = get_quran_verse()
        await channel.send(f"**Quran Verse of the Hour:**\n{quran_verse}")
    else:
        print(f"❌ Error: Channel {channel} is not a TextChannel!")

#ramadan command            
@bot.command(name="ramadan",
            aliases=['R'],
            help="this is help",
            description="this is description",
            brief="Say Ramadan Kareem to your fellas")
async def ramadan(ctx):
    await ctx.send("Ramadan Kareem! May this blessed month bring you peace and prosperity.")


#*remind command

@bot.command(name="remind",
             description="Remind you of futor or suhoor",
             help="Reminder",
             brief="Shows Remaining time of Maghrib and Fajr prayer")

async def remind(ctx):
    try:
        
        timings = get_prayer_time()  
    except Exception as e:
        await ctx.send(f"⚠️ Error fetching prayer times: {e}")
        return
    now = datetime.now()

    # Extract Maghrib and Fajr times 
    maghrib_time_str = timings.get("Maghrib", None)
    fajr_time_str = timings.get("Fajr", None)
    
    if not maghrib_time_str or not fajr_time_str: # Error handling
        await ctx.send("❌ Could not find Maghrib or Fajr prayer times.")
        return

    maghrib_time = datetime.strptime(maghrib_time_str, "%H:%M").replace(year=now.year, month=now.month, day=now.day)
    fajr_time = datetime.strptime(fajr_time_str, "%H:%M").replace(year=now.year, month=now.month, day=now.day)
    
    if now > fajr_time:
        fajr_time += timedelta(days=1)

    
    remaining_to_maghrib = maghrib_time - now if now < maghrib_time else timedelta(0)
    remaining_to_fajr = fajr_time - now

    
    def format_time(delta):
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{hours}h {minutes}m" if hours else f"{minutes}m"

    maghrib_msg = f"🕌 **Maghrib:** {format_time(remaining_to_maghrib)} remaining" if remaining_to_maghrib else "🕌 **Maghrib:** Already passed!"
    fajr_msg = f"🌙 **Fajr:** {format_time(remaining_to_fajr)} remaining"

    # Send response
    await ctx.send(f"{maghrib_msg}\n{fajr_msg}")

@bot.hybrid_command(name="prayertime", with_app_command=True, description="Show prayer times for today")
async def prayertime(ctx):
    try:
        timings = get_prayer_time()
    except Exception as e:
        await ctx.send(f"Sorry,Failed to fetch prayer times: {e}")
        return
    embeded_message = discord.Embed(title="Prayer time", description=f"Here are the prayer times for {datetime.now().strftime('%d-%m-%Y')}")
    embeded_message.set_thumbnail(url=ctx.author.avatar.url)
    embeded_message.set_image(url="https://cdn.discordapp.com/attachments/1337137910369226845/1344052506799636622/prayer.png?ex=67bf81f0&is=67be3070&hm=2f4a9cc085277f72cada5262bfb912b9133de32253adafaa1f061b75fbe0ba8a&")
    embeded_message.set_footer(text="Remember to pray on time!")
    embeded_message.add_field(name="Fajr", value=timings["Fajr"])
    embeded_message.add_field(name="Sunrise", value=timings["Sunrise"])
    embeded_message.add_field(name="Dhuhr", value=timings["Dhuhr"])
    embeded_message.add_field(name="Asr", value=timings["Asr"])
    embeded_message.add_field(name="Maghrib", value=timings["Maghrib"])
    embeded_message.add_field(name="Isha", value=timings["Isha"])

    await ctx.send(embed=embeded_message)


#Main entry
def main() -> None:
    
    bot.run(settings.TOKEN)
    logger.info(f"User:{bot.user}(ID ={bot.user.id})")

if __name__== '__main__':
    main()