import asyncio
import os
import re
from telethon import TelegramClient
from telethon.errors import FloodWaitError
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.types import Channel, Chat

API_ID = 21873991  # Replace with your Telegram API ID
API_HASH = "3a34f06f4f86d03a89b8d4345a70e27e"  # Replace with your Telegram API Hash
SESSION_NAME = "leak_downloader_session"

INITIAL_CHANNELS = [
    "Moonshine_Cloud",
    "ctinow",
    "cbanke"
]

MAX_CHANNELS = 10
#MAX_FILE_SIZE = 250 * 1024 * 1024  # 2MB

# Keywords to look for in messages or channel descriptions before joining
KEYWORDS = {
    "leak",
    "email",
    "credentials",
    "password",
    "ransomware",
    "breach",
    "exploit",
    "hack",
    "data dump",
    "dump",
    "dumped",
    "breached",
    "compromised",
    "database",
    "leaked"
}

LEAK_FILENAME_PATTERN = re.compile(r"(leak|email_leak|credentials|passwords).*\.txt$", re.IGNORECASE)
NEWS_LINK_PATTERN = re.compile(r"https?://\S+")

DOWNLOAD_DIR = "downloaded_leaks"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def print_info(msg): print(f"[INFO] {msg}")
def print_success(msg): print(f"[SUCCESS] {msg}")
def print_warning(msg): print(f"[WARNING] {msg}")
def print_error(msg): print(f"[ERROR] {msg}")

async def join_channel(client, channel):
    try:
        entity = await client.get_entity(channel)
        if isinstance(entity, (Channel, Chat)):
            if entity.username:
                await client(JoinChannelRequest(entity))
                print_success(f"Joined channel: {entity.title}")
                return entity
            else:
                print_warning(f"Private channel (no username), skipping join: {channel}")
                return None
        else:
            print_warning(f"Entity {channel} is not a channel or chat")
            return None
    except FloodWaitError as e:
        print_warning(f"Flood wait for {e.seconds} seconds while joining {channel}")
        await asyncio.sleep(e.seconds)
        return await join_channel(client, channel)
    except Exception as e:
        print_error(f"Failed to join {channel}: {e}")
        return None

async def check_channel_for_keywords(client, channel_username, keyword_set):
    """
    Fetch last few messages from channel WITHOUT joining to check for keywords.
    Returns True if any keyword found, else False.
    """
    try:
        entity = await client.get_entity(channel_username)
        # Can't iterate messages if private? So join first or just skip private channels.
        if not (isinstance(entity, (Channel, Chat)) and entity.username):
            print_warning(f"Skipping private or invalid channel {channel_username} for keyword scan")
            return False
        
        async for message in client.iter_messages(entity, limit=30):
            text = message.message or ""
            text_lower = text.lower()
            if any(kw in text_lower for kw in keyword_set):
                print_info(f"Keyword matched in channel {channel_username}: {text[:50]}...")
                return True
        return False
    except Exception as e:
        print_warning(f"Failed to check channel {channel_username} for keywords: {e}")
        return False

async def download_file(client, message, filename):
    try:
        path = os.path.join(DOWNLOAD_DIR, filename)
        if os.path.exists(path):
            print_info(f"File already exists, skipping download: {filename}")
            return
        await client.download_media(message, file=path)
        print_success(f"Downloaded file: {filename}")
    except Exception as e:
        print_error(f"Failed to download {filename}: {e}")

async def process_channel(client, channel_entity, joined_channels, to_join_channels, keyword_set):
    print_info(f"Scraping messages from channel: {channel_entity.title}")
    async for message in client.iter_messages(channel_entity, limit=200):
        if message.text:
            # Check for new channel links
            new_channels = re.findall(r't\.me/([a-zA-Z0-9_]+)', message.text)
            for ch in new_channels:
                ch_lower = ch.lower()
                if (ch_lower not in joined_channels and
                    ch_lower not in to_join_channels and
                    len(joined_channels) + len(to_join_channels) < MAX_CHANNELS):
                    
                    # Check if channel contains any keyword before joining
                    has_keywords = await check_channel_for_keywords(client, ch, keyword_set)
                    if has_keywords:
                        print_info(f"Adding new relevant channel to join: {ch}")
                        to_join_channels.add(ch_lower)
                    else:
                        print_info(f"Skipping channel {ch} — no keywords found")

            # Detect news links
            news_links = NEWS_LINK_PATTERN.findall(message.text)
            for link in news_links:
                print_info(f"Found news link: {link}")

        # Download leak files
        if message.document:
            filename = message.file.name or ""
            filesize = message.file.size or 0
            
            print_info(f"Found leak file: {filename} ({filesize} bytes), downloading...")
            await download_file(client, message, filename)

async def main():
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.start()

    joined_channels = set(ch.lower() for ch in INITIAL_CHANNELS)
    to_join_channels = set()

    # Join initial channels first
    for ch in INITIAL_CHANNELS:
        entity = await join_channel(client, ch)
        if entity:
            await process_channel(client, entity, joined_channels, to_join_channels, KEYWORDS)
        else:
            print_warning(f"Failed to join initial channel {ch}")

    # Join discovered channels that contain keywords
    while to_join_channels and len(joined_channels) < MAX_CHANNELS:
        ch = to_join_channels.pop()
        entity = await join_channel(client, ch)
        if entity:
            joined_channels.add(ch)
            await process_channel(client, entity, joined_channels, to_join_channels, KEYWORDS)
        else:
            print_warning(f"Skipping channel due to join failure: {ch}")

    print_success(f"Finished scraping. Joined {len(joined_channels)} channels.")

    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
