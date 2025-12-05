import requests
import time

def generate_image(prompt):
    # We clean the prompt to make it URL-safe
    clean_prompt = prompt.replace(" ", "%20")
    
    # We use Pollinations AI (Free, Fast, No Key needed)
    # Adding a timestamp ensures we get a unique image every time
    timestamp = int(time.time())
    image_url = f"https://image.pollinations.ai/prompt/{clean_prompt}?seed={timestamp}&width=1024&height=1024&nologo=true"
    
    return image_url