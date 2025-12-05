import requests
import re
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

def get_video_id(url):
    """Extracts the 'v' parameter from a YouTube URL"""
    if "youtu.be" in url:
        return url.split("/")[-1].split("?")[0]
    
    parsed = urlparse(url)
    if "youtube.com" in parsed.netloc:
        return parse_qs(parsed.query).get("v", [None])[0]
    return None

def get_video_metadata(video_id):
    """Fetches Title and Description if subtitles fail"""
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        # Fake a browser user-agent so YouTube lets us read the page
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            html = response.text
            # Simple Regex to find Title and Description
            title = re.search(r'<title>(.*?)</title>', html)
            desc = re.search(r'"shortDescription":"(.*?)"', html)
            
            title_text = title.group(1).replace("- YouTube", "") if title else "Unknown Title"
            desc_text = desc.group(1) if desc else "No description available."
            
            return f"Title: {title_text}\nDescription: {desc_text}"
        return None
    except Exception:
        return None

def get_transcript(video_url):
    """Fetches subtitles OR Metadata if subtitles fail"""
    video_id = get_video_id(video_url)
    if not video_id:
        return None
        
    try:
        # 1. Try to get the actual transcript
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        full_text = " ".join([item['text'] for item in transcript_list])
        return f"TRANSCRIPT:\n{full_text[:20000]}"
    except Exception:
        # 2. If that fails (No subtitles), get Metadata instead
        metadata = get_video_metadata(video_id)
        if metadata:
            return f"NO SUBTITLES FOUND. METADATA:\n{metadata}"
        return None