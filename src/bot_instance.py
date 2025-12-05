import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

# Load secrets
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Initialize Bot and Dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher()