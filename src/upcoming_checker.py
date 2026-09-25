import requests, re
from datetime import datetime
def get_today_events_detailed():
    r=requests.get("https://tinkerhub.org/events", timeout=15)
    today=datetime.now().strftime("%Y-%m-%d")
    today_str=datetime.now().strftime("%b %d")
    # upcoming section
    m=re.findall(r'href="(/events/[^"]+)"[^>]*>(.*?)</a>.*?(\d{1,2}:\d{2} [AP]M)', r.text, re.S)
    events=[]
    for path, title, time in m:
        if today_str.lower() in r.text.lower():
            # fetch host
            try:
                rr=requests.get("https://tinkerhub.org"+path, timeout=10)
                host=re.search(r'Hosts?</[^>]*>(.*?)</', rr.text)
                hostname=host.group(1).strip() if host else "TinkerHub"
                events.append({"path":path,"title":title.strip(),"host":hostname,"url":"https://tinkerhub.org"+path})
            except: pass
    return events
