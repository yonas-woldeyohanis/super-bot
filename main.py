import asyncio
import logging
import sys
from src.bot_instance import bot, dp
from src.handlers import router
from keep_alive import keep_alive

# Configure logging so we can see errors
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

async def main():
    # 1. Start the Flask Server (The "Heartbeat")
    keep_alive()
    print("--- Web Server Started ---")

    # 2. Register our handlers
    dp.include_router(router)

    # 3. Drop pending updates (prevents spam when bot restarts)
    await bot.delete_webhook(drop_pending_updates=True)
    
    # 4. Start polling
    print("--- Bot Started Polling ---")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped!")