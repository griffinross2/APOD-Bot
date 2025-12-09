import discord
import os
import io
import apod
from datetime import datetime, timedelta
from discord.ext import tasks

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

last_apod_title = ""

async def send_apod(channel, is_video, url, title, content):
    await channel.send(title)
    if is_video:
        await channel.send(content)
    else:
        await channel.send(file=discord.File(fp=io.BytesIO(content), filename="apod.jpg"))
    await channel.send(url)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    await client.change_presence(activity=discord.Game(name="apod:help for commands"))
    check_new_apod.start()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Help command
    if message.content.startswith('apod:help'):
        await message.channel.send('Commands:\n'
                                   'This bot will post the latest Astronomy Picture of the Day (APOD) from NASA in a channel named "apod" if available.\n'
                                   'apod:help - Show this help message\n'
                                   'apod:today - Get today\'s Astronomy Picture of the Day\n'
                                   'apod:latest - Get the latest Astronomy Picture of the Day\n'
                                   'apod:date [m/d/y] - Get the Astronomy Picture of the Day for the given date')

    # Today's APOD command
    if message.content.startswith('apod:today'):
        res = apod.fetch_apod_date()
        if res is None:
            await message.channel.send("No APOD has been released today.")
            return

        await send_apod(message.channel, res[0], res[1], res[2], res[3])
        
    # Latest APOD command
    if message.content.startswith('apod:latest'):
        res = apod.fetch_apod_url("https://apod.nasa.gov/")
        if res is None:
            await message.channel.send("The APOD website is not available.")
            return
        
        await send_apod(message.channel, res[0], res[1], res[2], res[3])

    # Specific date
    if message.content.startswith('apod:date'):
        message_args = message.content.split(' ')
        if len(message_args) < 2:
            await message.channel.send("Invalid arguments")
            return
        try:
            date = datetime.strptime(message_args[1], '%m/%d/%y')
        except ValueError:
            await message.channel.send("Invalid date")
            return
        res = apod.fetch_apod_date(date)
        if res is None:
            await message.channel.send("This APOD is not available.")
            return
        
        await send_apod(message.channel, res[0], res[1], res[2], res[3])


@tasks.loop(minutes=5)
async def check_new_apod():
    res = apod.fetch_apod_url("https://apod.nasa.gov/")
    if res is None:
        return
    
    global last_apod_title
    if res[2] != last_apod_title:
        # Avoid reposting the same APOD on bot restart
        if last_apod_title == "":
            last_apod_title = res[2]
            return
        
        last_apod_title = res[2]

        # Try to find an "apod" channel
        for guild in client.guilds:
            channel = discord.utils.get(guild.text_channels, name="apod")
            if channel:
                await send_apod(channel, res[0], res[1], res[2], res[3])
            else:
                # Try to send to the first text channel
                if len(guild.text_channels) > 0:
                    await send_apod(guild.text_channels[0], res[0], res[1], res[2], res[3])

token = os.getenv('BOT_TOKEN')
print(token)
client.run(token)