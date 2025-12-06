import requests
import os
from datetime import datetime
from src.web_search import search_web
from aiogram.types import FSInputFile
from src.ai_engine import transcribe_audio, get_ai_response 
from src.yt_utils import get_transcript
from aiogram import Router, F, Bot
from aiogram.types import Message, BufferedInputFile
from aiogram.filters import Command, CommandStart
from aiogram.enums import ParseMode
from aiogram.utils.chat_action import ChatActionSender
from src.doc_utils import read_pdf

# Import our engines
# from src.ai_engine import get_ai_response
from src.image_gen import generate_image

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot):
    user = message.from_user
    full_name = user.full_name
    username = f"@{user.username}" if user.username else "No Username"
    user_id = user.id
    language = user.language_code
    
    # 1. Send the Welcome Message to the User (The normal part)
    await message.answer(
        f"⚡️ <b>Yo, {user.first_name}!</b>\n\n"
        "I am <b>SuperBot</b>, your AI Powerhouse. 🧠\n"
        "I don't just talk — I <i>create</i>, <i>watch</i>, and <i>listen</i>.\n\n"
        "🔥 <b>WHAT I CAN DO:</b>\n\n"
        "🎨 <b>Visualize Ideas</b>\n"
        "<i>\"Draw a golden lion in space\"</i>\n\n"
        "📺 <b>Analyze Videos</b>\n"
        "<i>Send a YouTube link → I'll find the hidden facts.</i>\n\n"
        "📚 <b>Master Documents</b>\n"
        "<i>Upload a PDF → I'll become your study buddy.</i>\n\n"
        "🎤 <b>Voice Intelligence</b>\n"
        "<i>Talk to me → I listen and understand.</i>\n\n"
        "<b>Let's get to work. What's on your mind?</b> 🚀",
        parse_mode=ParseMode.HTML
    )

    # 2. Send the LOG to your Admin Group (The Secret part)
    log_group_id = os.getenv("LOG_GROUP_ID")
    
    if log_group_id:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_message = (
            f"🚨 <b>NEW USER ALERT</b>\n\n"
            f"👤 <b>Name:</b> {full_name}\n"
            f"🔗 <b>Username:</b> {username}\n"
            f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
            f"🌍 <b>Language:</b> {language}\n"
            f"🕒 <b>Time:</b> {timestamp}"
        )
        
        try:
            await bot.send_message(chat_id=log_group_id, text=log_message, parse_mode=ParseMode.HTML)
        except Exception as e:
            print(f"Failed to send log: {e}")

@router.message(Command("imagine"))
async def cmd_imagine(message: Message, bot: Bot):
    args = message.text.split(" ", 1)
    
    if len(args) < 2:
        await message.answer("⚠️ Please provide a prompt.\nExample: <code>/imagine a cyberpunk cat</code>", parse_mode=ParseMode.HTML)
        return

    user_prompt = args[1]
    status_msg = await message.answer(f"🎨 Generating: <b>{user_prompt}</b>...", parse_mode=ParseMode.HTML)
    
    async with ChatActionSender.upload_photo(bot=bot, chat_id=message.chat.id):
        try:
            # 1. Get the URL
            image_url = generate_image(user_prompt)
            
            # 2. DOWNLOAD the image first (Fixes the Telegram Error)
            response = requests.get(image_url)
            
            if response.status_code == 200:
                # 3. Create a file object from the bytes
                photo_file = BufferedInputFile(response.content, filename="image.jpg")
                
                # 4. Upload the bytes to Telegram
                await message.reply_photo(
                    photo=photo_file,
                    caption=f"✨ <b>Generated Art</b>\n\nPrompt: {user_prompt}",
                    parse_mode=ParseMode.HTML
                )
            else:
                await message.answer("❌ Error downloading image from AI server.")
            
            # 5. Cleanup
            await bot.delete_message(chat_id=message.chat.id, message_id=status_msg.message_id)

        except Exception as e:
            await message.answer(f"❌ Failed to generate image: {str(e)}")


@router.message(F.voice)
async def voice_handler(message: Message, bot: Bot):
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        
        # 1. Download Voice File
        file_id = message.voice.file_id
        file = await bot.get_file(file_id)
        file_path = f"voice_{file_id}.ogg"
        
        await bot.download_file(file.file_path, file_path)
        
        # 2. Transcribe (Voice -> Text)
        status_msg = await message.reply("👂 Listening...", parse_mode=ParseMode.HTML)
        user_text = transcribe_audio(file_path)
        
        # 3. Clean up
        if os.path.exists(file_path):
            os.remove(file_path)
            
        # 4. Error Handling
        if user_text.startswith("SYSTEM_ERROR"):
            await bot.edit_message_text(
                chat_id=message.chat.id, 
                message_id=status_msg.message_id, 
                text=f"❌ <b>Voice Error:</b>\n{user_text}",
                parse_mode=ParseMode.HTML
            )
            return

        # 5. Show user what we heard
        await bot.edit_message_text(
            chat_id=message.chat.id, 
            message_id=status_msg.message_id, 
            text=f"🗣️ <b>You said:</b> \"{user_text}\"",
            parse_mode=ParseMode.HTML
        )
        
        # 6. Ask the Brain
        user_id = message.from_user.id
        ai_reply = get_ai_response(user_text, user_id)
        
        # --- LOGIC BRANCHING ---
        
        # A. DRAW MODE
        if ai_reply.startswith("DRAW:"):
            image_prompt = ai_reply.replace("DRAW:", "").strip()
            await message.answer(f"🎨 Generating: <b>{image_prompt}</b>...", parse_mode=ParseMode.HTML)
            try:
                image_url = generate_image(image_prompt)
                response = requests.get(image_url)
                if response.status_code == 200:
                    photo_file = BufferedInputFile(response.content, filename="image.jpg")
                    await message.reply_photo(photo=photo_file, caption=f"✨ <b>Generated for you</b>", parse_mode=ParseMode.HTML)
                else:
                    await message.answer("❌ Error downloading image.")
            except Exception as e:
                await message.answer(f"❌ Failed to generate: {str(e)}")

        # B. SEARCH MODE (New!)
        elif ai_reply.startswith("SEARCH:"):
            search_query = ai_reply.replace("SEARCH:", "").strip()
            search_msg = await message.answer(f"🔍 Searching web for: <b>{search_query}</b>...", parse_mode=ParseMode.HTML)
            
            # Run the Search Tool
            search_results = search_web(search_query)
            
            if search_results:
                # Feed results back to AI
                follow_up_prompt = (
                    f"I searched the web for '{search_query}' and found this:\n\n"
                    f"{search_results}\n\n"
                    f"Instruction: Answer the user's original voice question based on these results. Keep it concise and spoken-style."
                )
                final_answer = get_ai_response(follow_up_prompt, user_id)
                
                # Send Final Answer
                await bot.delete_message(chat_id=message.chat.id, message_id=search_msg.message_id)
                try:
                    await message.answer(final_answer, parse_mode=ParseMode.MARKDOWN)
                except:
                    await message.answer(final_answer, parse_mode=None)
            else:
                await bot.edit_message_text(chat_id=message.chat.id, message_id=search_msg.message_id, text="❌ I looked online but couldn't find anything.")

        # C. NORMAL CHAT MODE
        else:
            try:
                await message.answer(ai_reply, parse_mode=ParseMode.MARKDOWN)
            except:
                await message.answer(ai_reply, parse_mode=None)
        

@router.message(F.document)
async def doc_handler(message: Message, bot: Bot):
    # Only process PDFs
    if message.document.mime_type != "application/pdf":
        await message.reply("📄 Please send me a <b>PDF</b> file.", parse_mode=ParseMode.HTML)
        return

    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        status_msg = await message.reply("📖 Reading document...", parse_mode=ParseMode.HTML)
        
        # 1. Download the PDF
        file_id = message.document.file_id
        file = await bot.get_file(file_id)
        file_path = f"doc_{file_id}.pdf"
        
        await bot.download_file(file.file_path, file_path)
        
        # 2. Extract Text
        doc_text = read_pdf(file_path)
        
        # 3. Clean up (Delete file)
        if os.path.exists(file_path):
            os.remove(file_path)
            
        if not doc_text:
            await bot.edit_message_text(chat_id=message.chat.id, message_id=status_msg.message_id, text="❌ Could not read text from this PDF.")
            return

        user_id = message.from_user.id
        doc_prompt = (
            f"I have uploaded a PDF document. Here is the content:\n"
            f"--- START OF DOCUMENT ---\n{doc_text}\n--- END OF DOCUMENT ---\n\n"
            f"Instruction: \n"
            f"1. Read this document carefully.\n"
            f"2. Give a clear, structured summary with bullet points and emojis.\n"
            f"3. Act like a supportive study buddy. Tell the user what the hardest concept is and offer to explain it simply.\n"
            f"4. End with a question like: 'Shall we dive deeper into Chapter 1?' or 'Want me to quiz you on this?'"
        )
        
        ai_reply = get_ai_response(doc_prompt, user_id)
        
        # 5. Reply to User
        await bot.edit_message_text(
            chat_id=message.chat.id, 
            message_id=status_msg.message_id, 
            text=f"✅ <b>Read Successfully!</b>\n\n{ai_reply}",
            parse_mode=ParseMode.MARKDOWN
        )


@router.message(F.text)
async def ai_chat_handler(message: Message, bot: Bot):
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        user_id = message.from_user.id
        user_text = message.text
        
        # --- NEW: Check for YouTube Link ---
        if "youtube.com" in user_text or "youtu.be" in user_text:
            # Notify user we are watching the video
            status = await message.answer("📺 Watching video... (Reading transcript)", parse_mode=ParseMode.HTML)
            
            # Try to get content
            video_text = get_transcript(user_text)
            
            if video_text:
                user_text = (
                    f"The user sent this YouTube video link: {user_text}\n"
                    f"Here is the content extracted from the video:\n{video_text}\n\n"
                    f"Instruction: \n"
                    f"1. Give a fun and concise summary of this video with emojis.\n"
                    f"2. Identify 3 interesting details or hidden facts in this video.\n"
                    f"3. At the end, ASK the user if they want to know more about a specific topic from the video. Be proactive!"
                )
                await bot.delete_message(chat_id=message.chat.id, message_id=status.message_id)
            else:
                # If no subtitles found, just let the AI chat normally
                await bot.edit_message_text(
                    chat_id=message.chat.id, 
                    message_id=status.message_id, 
                    text="⚠️ Couldn't read video captions. I'll try to answer based on the title/link only."
                )
        # -----------------------------------

        # 1. Ask the Brain (Now with Video Context if available)
        ai_reply = get_ai_response(user_text, user_id)
        
        # 2. Check for Image Generation (The "Draw" Tool)
        if ai_reply.startswith("DRAW:"):
            image_prompt = ai_reply.replace("DRAW:", "").strip()
            status_msg = await message.answer(f"🎨 On it! Generating: <b>{image_prompt}</b>...", parse_mode=ParseMode.HTML)
            try:
                image_url = generate_image(image_prompt)
                response = requests.get(image_url)
                if response.status_code == 200:
                    photo_file = BufferedInputFile(response.content, filename="image.jpg")
                    await message.reply_photo(photo=photo_file, caption=f"✨ <b>Generated for you</b>", parse_mode=ParseMode.HTML)
                else:
                    await message.answer("❌ Error downloading image.")
                await bot.delete_message(chat_id=message.chat.id, message_id=status_msg.message_id)
            except Exception as e:
                await message.answer(f"❌ Failed to generate: {str(e)}")
        
        else:
            # 3. Normal Text Reply (Summary or Chat)
            try:
                await message.answer(ai_reply, parse_mode=ParseMode.MARKDOWN)
            except Exception:
                await message.answer(ai_reply, parse_mode=None)