import requests, re, os, subprocess, json, time
from datetime import datetime
from config import GROQ_API_KEY, OPENROUTER_API_KEY, HF_TOKEN

# Uses Groq + OpenRouter + HF as second digest model
# 1. search tinkerhub web everyday
# 2. if event today -> find link -> poll for live -> after finished digest -> push

def search_today_events():
    try:
        r=requests.get("https://tinkerhub.org/events", timeout=15)
        today=datetime.now().strftime("%Y-%m-%d")
        # extract event links containing today date
        links=re.findall(r'href="(/events/[^"]+)"', r.text)
        return list(set(links))
    except Exception as e:
        print("search failed",e); return []

def find_stream_link(event_path):
    try:
        r=requests.get("https://tinkerhub.org"+event_path, timeout=10)
        # look for youtube / meet / live link
        m=re.search(r'(https?://(?:www\.)?(?:youtube\.com|youtu\.be|meet\.google\.com)[^"\s]+)', r.text)
        return m.group(1) if m else None
    except: return None

def wait_for_live_and_capture(stream_url, out="tmp/stream.mp4"):
    # poll every 5min if live, then capture after finished
    print(f"polling {stream_url} for live...")
    # simplified: yt-dlp --dump-json to check is_live, then download when not live (VOD)
    for i in range(36): # 3hrs
        try:
            j=json.loads(subprocess.check_output(["yt-dlp","--dump-json",stream_url], timeout=20))
            if j.get("is_live"):
                print("LIVE now, waiting to finish...")
            elif os.path.exists(out):
                break
            time.sleep(300)
        except: time.sleep(300)
    subprocess.run(["yt-dlp","-o",out, stream_url], check=False)

def digest_with_groq_openrouter(video="tmp/stream.mp4"):
    # Groq whisper + Groq vision + OpenRouter summary
    from groq import Groq
    client=Groq(api_key=GROQ_API_KEY)
    subprocess.run(["ffmpeg","-y","-i",video,"-vn","tmp/audio.wav"], check=False)
    with open("tmp/audio.wav","rb") as f:
        t=client.audio.transcriptions.create(model="whisper-large-v3", file=("audio.wav", f.read()))
    # frames every 10min
    frames=[]
    for ts in [300,900,1500,2100,2700,3300,3900,4500,5100]:
        out=f"tmp/frame_{ts}.jpg"
        subprocess.run(["ffmpeg","-y","-ss",str(ts),"-i",video,"-frames:v","1",out], check=False)
        if os.path.exists(out): frames.append(out)
    descs=[]
    import base64
    for f in frames[:5]:
        b64=base64.b64encode(open(f,"rb").read()).decode()
        r=client.chat.completions.create(model="qwen/qwen3.6-27b",
            messages=[{"role":"user","content":[
                {"type":"text","text":"Describe this TinkerHub event frame"},
                {"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}}]}])
        descs.append(r.choices[0].message.content)
    # summarize via OpenRouter
    import requests as req
    prompt=f"Transcript:{t.text[:6000]}\nVision:{descs}\nCreate markdown doc with title, summary, timestamps, tools, next steps."
    rr=req.post("https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization":f"Bearer {OPENROUTER_API_KEY}"},
        json={"model":"qwen/qwen-2.5-7b-instruct:free","messages":[{"role":"user","content":prompt}]}, timeout=60)
    text=rr.json()["choices"][0]["message"]["content"]
    out=f"docs/{datetime.now().strftime('%Y-%m-%d')}-groq.md"
    os.makedirs("docs",exist_ok=True)
    open(out,"w").write(text)
    print(f"groq digest -> {out}")
    # push to tinkerhub-event-documentation repo
    docs_repo=os.getenv("DOCS_REPO","safarhashim007/tinkerhub-event-documentation")
    tmp2="/tmp/docs_repo"
    subprocess.run(["rm","-rf",tmp2], check=False)
    subprocess.run(["git","clone",f"https://{os.getenv('GITHUB_TOKEN','') and f'x-access-token:{os.getenv(\"GITHUB_TOKEN\")}@' or ''}github.com/{docs_repo}.git", tmp2], check=False)
    if os.path.exists(tmp2):
        subprocess.run(["cp", out, tmp2+"/"], check=False)
        subprocess.run(["git","add","."], cwd=tmp2, check=False)
        subprocess.run(["git","-c","user.name=tinkerbot","-c","user.email=bot@tinkerhub.auto","commit","-m",f"doc {datetime.now().date()} detailed with host"], cwd=tmp2, check=False)
        subprocess.run(["git","push"], cwd=tmp2, check=False)
    # also push to own repo
    subprocess.run(["git","add",out], cwd="/home/tinkerspace/tinkerhub-auto-doc", check=False)
    subprocess.run(["git","commit","-m",f"auto-doc {datetime.now().date()}"], cwd="/home/tinkerspace/tinkerhub-auto-doc", check=False)
    subprocess.run(["git","push"], cwd="/home/tinkerspace/tinkerhub-auto-doc", check=False)
    return text

if __name__=="__main__":
    links=search_today_events()
    print("today links",links)
    for p in links:
        url=find_stream_link(p)
        if url:
            print("found stream",url)
            wait_for_live_and_capture(url)
            digest_with_groq_openrouter()
