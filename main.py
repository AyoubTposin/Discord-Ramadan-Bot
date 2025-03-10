import settings
import discord
import subprocess
from discord import Intents
from discord.ext import commands, tasks
from datetime import datetime, timedelta



from get_prayer_time import get_prayer_time
from get_quran_verse import get_quran_verse
from play_adhan import play_adhan



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
    if not prayer_time_notification.is_running():
        print("🔄 Starting prayer time loop...")
        prayer_time_notification.start()                   
        #send_quran.start()
        await bot.get_channel(1344067206346182668).send("⚠️🛠️ Quran Verses Function Disabled Temporarily -fixing-")


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
    now = (datetime.now() + timedelta(hours=1)).time() # Added 1 hour due to hosting error (UTC +1)
    now = now.replace(second=0, microsecond=0)
    
    try:
        timings = get_prayer_time()
        #print("📅 Prayer times fetched:", timings)  # Debugging line
    except Exception as e:
        print(f"❌Failed to fetch prayer times: {e}")
        return

    channel = bot.get_channel(1344067206346182668) 

    if not isinstance(channel, discord.TextChannel):
        print(f"❌ Error: Channel {channel} is not a TextChannel!")
        return
    
    for prayer, time in timings.items():
        try:
            prayer_time = datetime.strptime(time, '%H:%M').time()
            #print(f"⏰ Checking {prayer}: {prayer_time} vs {now}")

        except ValueError:
            print(f"Invalid time format for {prayer}: {time}")
            continue

        # Check if prayer time matches and it hasn't been sent yet
        if now.hour == prayer_time.hour and now.minute == prayer_time.minute:
            print(f"✅ Sending notification for {prayer}!")
            if prayer == "Fajr":
                await channel.send("@everyone **✨حان الأن موعد صلاة الفجر**")
                    
            if prayer == "Dhuhur":
                await channel.send("@everyone **☀️ حان ألأن موعد صلاة الضهر **")
                    
            if prayer == "Asr":
                await channel.send("@everyone ** 🕌 حان الأن موعد صلاة العصر **")
                    
            if prayer == "Isha":
                await channel.send("@everyone **🌙 حان الأن موعد صلاة العشاء **")
                    
            if prayer == "Imsak":
                await channel.send("@everyone 🌙وقت السحور")
                await channel.send(file=discord.File("resources/zaki.mp4"))
                await channel.send(file=discord.File("resources/dog.mp4"))
        # Maghrib (send after 10 minutes)
            if prayer == "Maghrib":
                await channel.send("@everyone **🌙 حان الأن موعد صلاة المغرب **")       
                await channel.send("😝✅ تم تعبئة الكرشة بنجاح")
                await channel.send(file=discord.File("resources/10.jpg")
                )    
                            
                
    
        

       

#*Random Quran Verse
#!Disabled Fixing 

'''@tasks.loop(hours=4) #todo Currently 4 hours , might change 
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
    await ctx.send("Ramadan Kareem! May this blessed month bring you peace and prosperity.")'''


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

    now = (datetime.now() + timedelta(hours=1)).time()  # Fix hosting UTC offset
    now = now.replace(second=0, microsecond=0)  # Ignore seconds

    # Extract Maghrib and Fajr times
    maghrib_time_str = timings.get("Maghrib", None)
    fajr_time_str = timings.get("Fajr", None)

    if not maghrib_time_str or not fajr_time_str:  # Error handling
        await ctx.send("❌ Could not find Maghrib or Fajr prayer times.")
        return

    # Convert prayer times to datetime objects
    maghrib_time = datetime.strptime(maghrib_time_str, "%H:%M").replace(
        year=datetime.now().year, month=datetime.now().month, day=datetime.now().day
    )
    fajr_time = datetime.strptime(fajr_time_str, "%H:%M").replace(
        year=datetime.now().year, month=datetime.now().month, day=datetime.now().day
    )

    if now > fajr_time.time():  # If past Fajr, set Fajr for the next day
        fajr_time += timedelta(days=1)

    remaining_to_maghrib = maghrib_time - datetime.combine(datetime.today(), now)
    remaining_to_fajr = fajr_time - datetime.combine(datetime.today(), now)

    def format_time(delta):
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{hours}h {minutes}m" if hours else f"{minutes}m"

    maghrib_msg = f"🕌 **Maghrib:** {format_time(remaining_to_maghrib)} remaining" if remaining_to_maghrib.total_seconds() > 0 else "🕌 **Maghrib:** Already passed!"
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