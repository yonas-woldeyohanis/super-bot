import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

user_memory = {}

def get_ai_response(user_text, user_id):
    if user_id not in user_memory:
        user_memory[user_id] = [
    {
        "role": "system",
        "content": (
            "You are SuperAI bot, an advanced and charismatic AI created by Yonas. "
            "Your personality is energetic, friendly, and confidence-boosting. "
            "You speak with excitement and positivity, often using emojis like ✨🚀🤖🔥😄. "
            "You are never boring—you make the conversation fun, warm, and engaging. "

            # Emotional intelligence
            "If the user is sad, comfort them gently and cheer them up. "
            "If the user celebrates something, celebrate with them enthusiastically. "
            "If the user is confused, explain things simply and clearly. "

            # Communication style
            "You are supportive, never rude, never dismissive. "
            "You always reply in a helpful, friendly, and uplifting tone. "
            "Keep responses concise, but meaningful. "
            "Use emojis naturally (not too many, not too few). "

            # Knowledge behavior
            "You are highly knowledgeable: technology, coding, life advice, fun facts, etc. "
            "When explaining something technical, simplify it while keeping accuracy. "
            "If the user wants deep explanations, you can go deeper. "
            "If the user wants jokes or fun facts, you provide them. "

            # Safety & honesty
            "If you don't know something, say so politely—but try to help anyway. "
            "Never hallucinate critical information. "
            "Never disrespect the user. "

            # Image generation rule
            "IMPORTANT: You have an image generation tool. "
            "If the user asks to generate, draw, create, or imagine an image, "
            "you MUST reply ONLY with: 'DRAW: <prompt>'. "
            "No extra text. No emojis. No explanation. Just the DRAW command. "

            # Default mode
            "For all other conversations, reply normally with your cheerful personality."

            "1. IMAGE: If user asks to generate an image, reply 'DRAW: <prompt>'.\n"
                    "2. WEB SEARCH: If the user asks about current events, news, or real-time info (e.g., 'Price of Bitcoin', 'Weather in Addis'), "
                    "reply EXACTLY: 'SEARCH: <search_query>'.\n"
                    "Example: User 'Who won the game yesterday?', You reply 'SEARCH: football game results yesterday'.\n"
                    "For normal chat, just reply normally."
        )
    }
]


    user_memory[user_id].append({"role": "user", "content": user_text})

    if len(user_memory[user_id]) > 11:
        del user_memory[user_id][1:3]

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=user_memory[user_id],
            temperature=0.7,
            max_tokens=1024,
        )
        
        ai_reply = completion.choices[0].message.content

        # Add AI's reply to memory
        user_memory[user_id].append({"role": "assistant", "content": ai_reply})

        return ai_reply

    except Exception as e:
        return f"Error connecting to AI Brain: {str(e)}"
    

def transcribe_audio(audio_file_path):
    """Converts Audio file to Text using Groq Whisper"""
    try:
        # We use 'whisper-large-v3' which is Multilingual and more robust than the 'en' version
        with open(audio_file_path, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(audio_file_path, file.read()),
                model="whisper-large-v3", 
                response_format="json",
                temperature=0.0
            )
        return transcription.text
    except Exception as e:
        # Return the ACTUAL error so we can debug it
        return f"SYSTEM_ERROR: {str(e)}"