import requests, re
from datetime import datetime

def has_event_today():
    # generic check: scrape tinkerhub events or calendar
    try:
        r=requests.get("https://tinkerhub.org/events", timeout=10)
        today=datetime.now().strftime("%b %d").lower()
        # if today string appears near event card, assume event
        return today in r.text.lower()
    except: return False

def is_youtube_live(channel_url):
    if not channel_url: return False
    try:
        # yt-dlp can probe without download
        import subprocess, json
        out=subprocess.check_output(["yt-dlp","--dump-json", channel_url], timeout=15)
        info=json.loads(out)
        return info.get("is_live", False)
    except: return False
