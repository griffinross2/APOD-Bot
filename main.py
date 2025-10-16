import discord
import os
import apod
from datetime import datetime, timedelta

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Help command
    if message.content.startswith('apod:help'):
        await message.channel.send('Test')

    # Today's APOD command
    if message.content.startswith('apod:today'):
        res = apod.fetch_apod_date()
        if res is None:
            await message.channel.send("No APOD has been released today.")
        else:
            await message.channel.send(res[0] + '\n' + res[1])    
        
    # Latest APOD command
    if message.content.startswith('apod:latest'):
        date = datetime.now()
        res = None

        res = apod.fetch_apod_url("https://apod.nasa.gov/")

        if res is None:
            await message.channel.send("The APOD website is not available.")
        else:
            description = "APOD "
            await message.channel.send(res[0] + '\n' + res[1])

token = os.getenv('BOT_TOKEN')
print(token)
client.run(token)