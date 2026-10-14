import discord
import os
import io
import requests
import apod
from datetime import datetime, timedelta
from discord.ext import tasks
from dotenv import load_dotenv
import traceback

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

last_apod_title = ""

async def send_apod(channel, title, img_url, explanation, article_url):
    # await channel.send(title)

    # if img_url is not None:
    #     # Try to download the image
    #     try:
    #         response = requests.get(img_url)
    #         response.raise_for_status()
    #         content = response.content
    #         await channel.send(file=discord.File(fp=io.BytesIO(content), filename="apod.jpg"))
    #     except Exception as e:
    #         print(f"Error downloading APOD image: {e}")

    # await channel.send(explanation)
    await channel.send(article_url)

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
        try:
            res = apod.apod_api_req(os.getenv('NASA_API_KEY'), date=datetime.now())
            await send_apod(message.channel, res['title'], res['hdurl'], res['explanation'], res['link'])
        except Exception as e:
            print(f"Error fetching today's APOD: {e}")
            traceback.print_exc()

            await message.channel.send(f"Error fetching today's APOD")
            return

        
    # Latest APOD command
    if message.content.startswith('apod:latest'):
        try:
            res = apod.apod_api_req(os.getenv('NASA_API_KEY'), date=datetime.now())
            await send_apod(message.channel, res['title'], res['hdurl'], res['explanation'], res['link'])
        except Exception as e:
            print(f"Error fetching latest APOD: {e}")
            traceback.print_exc()

            await message.channel.send(f"Error fetching latest APOD")
            return

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
        try:
            res = apod.apod_api_req(os.getenv('NASA_API_KEY'), date=date)
            await send_apod(message.channel, res['title'], res['hdurl'], res['explanation'], res['link'])
        except Exception as e:
            print(f"Error fetching APOD for date {date}: {e}")
            traceback.print_exc()

            await message.channel.send(f"Error fetching APOD")
            return


@tasks.loop(minutes=5)
async def check_new_apod():
    try:
        res = apod.apod_api_req(os.getenv('NASA_API_KEY'))
    
        global last_apod_title
        if res['title'] != last_apod_title:
            # Avoid reposting the same APOD on bot restart
            if last_apod_title == "":
                last_apod_title = res['title']
                return
            
            last_apod_title = res['title']

            # Try to find an "apod" channel
            for guild in client.guilds:
                channel = discord.utils.get(guild.text_channels, name="apod")
                if channel:
                    await send_apod(channel, res['title'], res['hdurl'], res['explanation'], res['link'])
                else:
                    # Try to send to the first text channel
                    if len(guild.text_channels) > 0:
                        await send_apod(guild.text_channels[0], res['title'], res['hdurl'], res['explanation'], res['link'])

    except Exception as e:
        print(f"Error checking for new APOD: {e}")

token = os.getenv('BOT_TOKEN')
print(token)
client.run(token)