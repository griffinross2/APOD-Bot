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
                                   'apod:latest - Get the latest Astronomy Picture of the Day')

    # Today's APOD command
    if message.content.startswith('apod:today'):
        res = apod.fetch_apod_date()
        if res is None:
            await message.channel.send("No APOD has been released today.")
            return

        await message.channel.send(res[1])
        await message.channel.send(file=discord.File(fp=io.BytesIO(res[2]), filename="apod.jpg"))
        await message.channel.send(res[0])
        
    # Latest APOD command
    if message.content.startswith('apod:latest'):
        res = apod.fetch_apod_url("https://apod.nasa.gov/")
        if res is None:
            await message.channel.send("The APOD website is not available.")
            return
        
        await message.channel.send(res[1])
        await message.channel.send(file=discord.File(fp=io.BytesIO(res[2]), filename="apod.jpg"))
        await message.channel.send(res[0])

@tasks.loop(minutes=5)
async def check_new_apod():
    res = apod.fetch_apod_url("https://apod.nasa.gov/")
    if res is None:
        return
    
    global last_apod_title
    if res[1] != last_apod_title:
        # Avoid reposting the same APOD on bot restart
        if last_apod_title == "":
            last_apod_title = res[1]
            return
        
        last_apod_title = res[1]

        # Try to find an "apod" channel
        for guild in client.guilds:
            channel = discord.utils.get(guild.text_channels, name="apod")
            if channel:
                await channel.send(res[1])
                await channel.send(file=discord.File(fp=io.BytesIO(res[2]), filename="apod.jpg"))
                await channel.send(res[0])
            else:
                # Try to send to the first text channel
                if len(guild.text_channels) > 0:
                    await guild.text_channels[0].send(res[1])
                    await guild.text_channels[0].send(file=discord.File(fp=io.BytesIO(res[2]), filename="apod.jpg"))
                    await guild.text_channels[0].send(res[0])

token = os.getenv('BOT_TOKEN')
print(token)
client.run(token)