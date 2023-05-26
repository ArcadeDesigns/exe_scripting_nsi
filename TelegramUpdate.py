import os
import sys
import asyncio
from telethon import TelegramClient
import telegram
from telegram.ext import Updater, MessageHandler, CommandHandler

class TelegramUpdate:
    def __init__(self):
        self.telegram_messages = []

    def init(self):
        # Create a Telegram client
        self.client = TelegramClient('session_name', api_id='28136536', api_hash='f0b27aea82af77aed15596e9eb939cce')

        # Connect to Telegram servers
        try:
            self.client.start()
        except Exception as e:
            print("Error: " + str(e))
            return

        # Get the messages from the channel
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.get_messages())
        self.client.disconnect()

    async def get_messages(self):
        message_found = False
        messages = await self.client.get_messages('https://t.me/ebire_fx_forex_trading', limit=10)
        try:
            for message in messages:
                telegram_signal = ""
                telegram_currency = ""
                telegram_entry = ""
                telegram_entry_time = ""

                message_parts = message.message.split(',')
                for part in message_parts:
                    if "Signal:" in part:
                        telegram_signal = part.split(":")[1].strip()
                    if "Currency:" in part:
                        telegram_currency = part.split(":")[2].strip()
                    if "Entry Price:" in part:
                        telegram_entry = part.split(":")[3].strip()
                    if "Entry Time:" in part:
                        telegram_entry_time = part.split(":")[4].strip()
                        message_found = True
                        break

                if message_found:
                    self.telegram_messages.append({
                        'Signal': telegram_signal,
                        'Currency': telegram_currency,
                        'Entry': telegram_entry,
                        'Time': telegram_entry_time
                    })
                    message_found = False

            if not message_found:
                self.telegram_messages.append({
                    'Signal': "Subscribe <br> to our <br> Premium <br> Version",
                    'Currency': "Not Available",
                    'Entry': "Not Available",
                    'Time': "Not Available"
                })

        except Exception as e:
            print("Error: " + str(e))

    def get_latest_message(self):
        return self.telegram_messages

if __name__ == '__main__':
    tc = TelegramUpdate()
    tc.init()
    messages = tc.get_latest_message()
    for i, message in enumerate(messages[:4]):
        print(f"Message_{i+1}:")
        print(f"Signal: {message['Signal']}")
        print(f"Currency: {message['Currency']}")
        print(f"Entry: {message['Entry']}")
        print(f"Time: {message['Time']}")
        print()
