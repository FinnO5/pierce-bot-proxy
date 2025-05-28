import os
import random 
import json

import asyncio
from aiohttp import web
from aiohttp import web, ClientSession
import aiohttp

import discord
from dotenv import load_dotenv  # Used to load environment variables from a .env file
from discord.ext import commands


DEFAULT_CHANNEL_ID = 0#put the id of the channel you want the bot to defult to here, it will go here if there is nothing in bound_channel_id.txt

# Name of the file used to store the bound channel ID
CHANNEL_ID_FILE = "bound_channel_id.txt"


def get_stored_bound_channel_id():
    # Retrieve the bound channel ID from a local file, or use the default if not found
    try:
        with open(CHANNEL_ID_FILE, "r") as f:
            contents = f.read().strip()
            if contents:
                return int(contents)
    except FileNotFoundError:
        pass
    return DEFAULT_CHANNEL_ID


def write_channel_id_file(new_id: int) -> bool:
    try:
        # Write the new channel ID to the file
        with open(CHANNEL_ID_FILE, "w") as f:
            f.write(str(new_id))

        # Read the file again to verify the write was successful
        with open(CHANNEL_ID_FILE, "r") as f:
            saved_id = f.read().strip()
            if saved_id == str(new_id):
                return True
    except Exception as e:
        print(f"Error setting channel ID: {e}")
    
    return False


# Default number of messages to retrieve for recent history
user_prefrence_for_amount_of_near_end_hisotry = 5


# Load token and guild ID from environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)


# Initialize the aiohttp web application
app = web.Application()
routes = web.RouteTableDef()


async def get_near_end_history(amount_of_messages="defult"):
    """
    Retrieve the most recent messages from the currently bound channel.
    Uses the user preference unless overridden.
    """
    global user_prefrence_for_amount_of_near_end_hisotry
    print("Fetching recent message history. Message count:", amount_of_messages)
    
    if amount_of_messages != "defult":
        # Update the user preference with the specified number of messages
        user_prefrence_for_amount_of_near_end_hisotry = amount_of_messages

    channel = bound_channel
    messages = []

    async for msg in channel.history(limit=user_prefrence_for_amount_of_near_end_hisotry):
        messages.append({
            "username": msg.author.name,
            "avatar": msg.author.display_avatar.url,
            "timestamp": msg.created_at.isoformat(timespec='seconds'),
            "content": msg.content
        })  # Necessary message info for the web app

    return messages


async def post_message_data_to_flask(data_dict):
    """
    Send a POST request to the local Flask server with message data.
    """
    url = 'http://localhost:5000/bot_forced_update'
    try:
        async with ClientSession() as session:
            async with session.post(url, json=data_dict) as resp:
                response_text = await resp.text()
                print(f"✅ Successfully posted data to {url}, response: {response_text}")
                return response_text
    except Exception as e:
        print(f"❌ Failed to post data to {url}: {e}")
        return None


@routes.post('/send_message_pb')
async def new_event(request):
    """
    HTTP endpoint to receive a message from an external source and post it to the bound Discord channel.
    """
    data = await request.json()
    msg = data.get("message", "")
    print("✅ Received message:", msg)
    channel = bound_channel
    await channel.send(msg)
    return web.Response(text="ok")


@routes.get('/get_chat_history')
async def get_chat_history(request):
    """
    HTTP endpoint to return recent chat history in JSON format.
    Expects a query parameter 'amt_messages' to determine how many messages to return.
    """
    amount_of_messages_str = request.rel_url.query.get('amt_messages')

    try:
        amt_messages = int(amount_of_messages_str)
    except ValueError:
        return web.json_response({'error': 'amt_messages must be an integer'}, status=400)

    messages = await get_near_end_history(amt_messages)
    return web.json_response(messages, dumps=lambda x: json.dumps(x, indent=4))


app.add_routes(routes)


async def run_web():
    """
    Start the local aiohttp web server to enable HTTP communication.
    """
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 5001)
    await site.start()
    print("🚀 Server started on http://localhost:5001")


@bot.event
async def on_ready():
    """
    Event triggered when the bot is fully connected and ready.
    Binds the bot to the stored channel and starts the web server.
    """
    global bound_channel
    bound_channel = bot.get_channel(get_stored_bound_channel_id())
    bot.loop.create_task(run_web())
    await bound_channel.send("My program just started up. I am connected to this channel.")


@bot.event
async def on_message(message):
    """
    Event triggered on every message received.
    Forwards messages to the web app, excluding those sent by the bot itself.
    """
    await bot.process_commands(message)
    print("User said:", message.content)

    if message.author == bot.user:
        return
    else:
        # Retrieve recent message history and send it to the Flask server
        messages = await get_near_end_history()
        await post_message_data_to_flask({"messages": messages})


@bot.command()
async def bind(ctx):
    """
    Command to bind the bot to the current channel.
    This channel will be used for all future message history operations.
    """
    global bound_channel
    bound_channel = ctx.channel

    success = write_channel_id_file(ctx.channel.id)

    await ctx.send(f"Hey {ctx.author.display_name}, I have bound myself to this channel ({ctx.channel.name}). "
                   "Messages will now be routed here and this will be used as the source of chat history for the UI.")

    if not success:
        await ctx.send("⚠️ However, I was unable to save this binding to the local cache. "
                       "The binding will be lost on restart. Try using `!bind` again.")
        await ctx.send("If this issue persists, please contact the developer or check the server configuration.")

    # Send an initial update to the UI with the current message history
    messages = await get_near_end_history()
    await post_message_data_to_flask({"messages": messages})


bot.run(TOKEN)
