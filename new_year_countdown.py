import datetime
import pytz
import asyncio
from telethon import TelegramClient
from dotenv import load_dotenv
import os

load_dotenv()

API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
PHONE_NUMBER = os.getenv('PHONE_NUMBER')
USER_ID = os.getenv('USER_ID')  # Keep USER_ID as string

if None in (API_ID, API_HASH, PHONE_NUMBER, USER_ID):
    raise ValueError("Missing environment variables")

india_tz = pytz.timezone('Asia/Kolkata')
now = datetime.datetime.now(india_tz)
print(f"🌐 Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}")

new_year = datetime.datetime(now.year + 1, 1, 1, 0, 0, 0, tzinfo=india_tz)
print(f"🎉 New Year time: {new_year.strftime('%Y-%m-%d %H:%M:%S')}")

client = TelegramClient('wish', API_ID, API_HASH)

stop_update = False

async def send_initial_message():
    message = "Hey Jyoti! 🌟 New Year is almost here. Let’s start the countdown together! 🎉"
    try:
        entity = await client.get_entity(int(USER_ID))
        sent_message = await client.send_message(entity, message)
        print("📩 Initial Message Sent")
        return sent_message
    except Exception as e:
        print(f"❌ Failed to send initial message: {e}")
        return None

async def countdown_and_wish(sent_message):
    global stop_update
    try:
        countdown_time = 10
        while countdown_time > 0:
            countdown_message = f"Just {countdown_time} seconds left! 🕛 Ready to welcome an amazing year? 😊"
            await client.edit_message(sent_message, countdown_message)
            print(f"⏳ Countdown: {countdown_time} seconds remaining")
            await asyncio.sleep(1)
            countdown_time -= 1

        final_message = (
            "<b>🌸 HAPPY NEW YEAR, JYOTI! 🌸</b>\n\n"
            "<i>✨ A new year means new chances to shine brighter than ever! I know you're going to do amazing things this year. 🏆</i>\n\n"
            "<i>💪 Stay focused, keep working hard, and make every moment count. I'm always here cheering for you!</i>\n\n"
            "<i>Let’s make this moment unforgettable. 😌✨</i>"
        )
        gif_path = "wish.gif"
        await client.send_file(sent_message.to_id, gif_path, caption=final_message, parse_mode="html")
        await client.delete_messages(sent_message.to_id, [sent_message.id])
        print("🎆 Final Message and GIF Sent, Countdown Messages Deleted")
    except Exception as e:
        print(f"❌ Failed to send final message: {e}")
    finally:
        stop_update = True

async def main():
    await client.start()

with client:
    client.loop.run_until_complete(main())

time_to_wait = (new_year - datetime.datetime.now(india_tz)).total_seconds() - 15

async def update_terminal_time():
    global stop_update
    while not stop_update:
        now = datetime.datetime.now(india_tz)
        time_remaining = new_year - now
        hours, remainder = divmod(time_remaining.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        print(f"⏰ Time remaining until New Year: {int(hours)}h {int(minutes)}m {int(seconds)}s", end="\r")
        await asyncio.sleep(1)

async def start_countdown():
    await asyncio.sleep(time_to_wait)
    sent_message = await send_initial_message()
    if sent_message:
        await asyncio.sleep(5)
        await countdown_and_wish(sent_message)

with client:
    client.loop.run_until_complete(asyncio.gather(update_terminal_time(), start_countdown()))