from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode

# Create a router (think of it as a blueprint for routes)
router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    user_name = message.from_user.first_name
    await message.answer(
        f"Yo <b>{user_name}</b>! 🚀\n\n"
        "I am your new Advanced AI Assistant.\n"
        "Currently running on the cloud via Render.",
        parse_mode=ParseMode.HTML
    )

# This catches all text messages (The entry point for our AI)
@router.message(F.text)
async def ai_chat_handler(message: Message):
    user_text = message.text
    
    # Placeholder: In the next step, we connect GPT/Llama here
    # For now, let's just show it's working
    response = f"<i>You said:</i> {user_text}\n\n(AI Brain coming in next update...)"
    
    await message.answer(response, parse_mode=ParseMode.HTML)