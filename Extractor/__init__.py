import asyncio
import logging
from pyrogram import Client, idle
from config import API_ID, API_HASH, BOT_TOKEN
import os
import sys

# Create base directory for all data
BASE_DIR = os.path.join(os.path.expanduser("~"), ".extractor_bot")
SESSION_DIR = os.path.join(BASE_DIR, "sessions")

# Ensure directories exist with proper permissions
try:
    os.makedirs(SESSION_DIR, mode=0o700, exist_ok=True)
except Exception as e:
    print(f"Error creating directories: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

# Initialize event loop
loop = asyncio.get_event_loop()

# Initialize Pyrogram client with proper session path
try:
    app = Client(
        os.path.join(SESSION_DIR, "extractor_bot"),
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
        sleep_threshold=120,
        workers=500
    )
except Exception as e:
    logger.error(f"Failed to initialize client: {e}")
    sys.exit(1)

async def info_bot():
    global BOT_ID, BOT_NAME, BOT_USERNAME
    try:
        await app.start()
        getme = await app.get_me()
        BOT_ID = getme.id
        BOT_USERNAME = getme.username
        if getme.last_name:
            BOT_NAME = getme.first_name + " " + getme.last_name
        else:
            BOT_NAME = getme.first_name
        await idle()
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        sys.exit(1)

# Run the bot
loop.run_until_complete(info_bot())

