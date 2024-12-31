import datetime
import pytz
import asyncio
from telethon import TelegramClient
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
PHONE_NUMBER = os.getenv('PHONE_NUMBER')
USER_ID = os.getenv('USER_ID')  # Keep USER_ID as string

if None in (API_ID, API_HASH, PHONE_NUMBER, USER_ID):
    raise ValueError("One or more environment variables are missing")

# Define your local time zone
india_tz = pytz.timezone('Asia/Kolkata')

# Get the current time in your local time zone
now = datetime.datetime.now(india_tz)
print(f"🌐 Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}")

# Define the New Year time
new_year = datetime.datetime(now.year + 1, 1, 1, 0, 0, 0, tzinfo=india_tz)
print(f"🎉 New Year time: {new_year.strftime('%Y-%m-%d %H:%M:%S')}")

# Initialize the Telegram Client
client = TelegramClient(PHONE_NUMBER, API_ID, API_HASH)

stop_update = False

async def send_initial_message():
    message = "Hey Jyoti! Let's start the countdown to the new year!"
    try:
        # Fetch the user entity using get_entity method
        entity = await client.get_entity(int(USER_ID))
        # Send the initial message
        sent_message = await client.send_message(entity, message)
        print("📩 Initial Message Sent")
        return sent_message
    except Exception as e:
        print(f"❌ Failed to send initial message: {e}")
        return None

async def countdown_and_wish(sent_message):
    global stop_update
    try:
        countdown_time = 10  # Countdown duration in seconds
        while countdown_time > 0:
            # Update the message with the countdown
            countdown_message = f"Only {countdown_time} seconds left! Get ready to welcome the new year!"
            await client.edit_message(sent_message, countdown_message)
            print(f"⏳ Countdown: {countdown_time} seconds remaining")
            await asyncio.sleep(1)
            countdown_time -= 1

        # Send the final New Year wish and delete the previous countdown messages
        final_message = (
            "*HAPPY NEW YEAR, JYOTI!*\n\n"
            "A new year means a new chapter, new dreams, and new opportunities. "
            "I’m so grateful to know someone as inspiring as you. Here's to all your big dreams coming true this year!\n\n"
            "Remember, every step you take brings you closer to your goals. "
            "I'll be cheering for you every step of the way!\n\n"
            "Here's to an incredible 2025!"
        )
        await client.send_message(sent_message.to_id, final_message, parse_mode="Markdown")
        await client.delete_messages(sent_message.to_id, [sent_message.id])
        print("🎆 Final Message Sent and Countdown Messages Deleted")
    except Exception as e:
        print(f"❌ Failed to send final message: {e}")
    finally:
        stop_update = True

async def main():
    await client.start()
    # Removed dialog printing for cleaner output

# Run the dialog verification
with client:
    client.loop.run_until_complete(main())

# Calculate the time to wait until 10 seconds before midnight
time_to_wait = (new_year - datetime.datetime.now(india_tz)).total_seconds() - 10

# Continuously update the remaining time in the terminal
async def update_terminal_time():
    global stop_update
    while not stop_update:
        now = datetime.datetime.now(india_tz)
        time_remaining = new_year - now
        hours, remainder = divmod(time_remaining.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        print(f"⏰ Time remaining until New Year: {int(hours)}h {int(minutes)}m {int(seconds)}s", end="\r")
        await asyncio.sleep(1)

# Run the initial message sending and countdown process
async def start_countdown():
    await asyncio.sleep(time_to_wait)
    sent_message = await send_initial_message()
    if sent_message:
        await countdown_and_wish(sent_message)

# Run the update_terminal_time and start_countdown coroutines concurrently
with client:
    client.loop.run_until_complete(asyncio.gather(update_terminal_time(), start_countdown()))