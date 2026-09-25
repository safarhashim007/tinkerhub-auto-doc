"""Hybrid pipeline: audio-first Whisper (Groq) -> highlight timestamps -> vision (Groq qwen3) -> doc (Gemini)"""
import os, subprocess, json, base64
from config import GROQ_API_KEY, GEMINI_API_KEY

def extract_audio(video="tmp/stream.mp4", out="tmp/audio.wav"):
    subprocess.run(["ffmpeg","-y","-i",video,"-vn",out], check=True)

def transcribe_groq(audio="tmp/audio.wav"):
    from groq import Groq
    client=Groq(api_key=GROQ_API_KEY)
    with open(audio,"rb") as f:
        t=client.audio.transcriptions.create(model="whisper-large-v3", file=(audio,f.read()))
    open("tmp/transcript.json","w").write(json.dumps({"text":t.text}))
    return t.text

def extract_frames(video="tmp/stream.mp4", timestamps=[300,600,900]):
    for ts in timestamps:
        out=f"tmp/frame_{ts}.jpg"
        subprocess.run(["ffmpeg","-y","-ss",str(ts),"-i",video,"-frames:v","1",out], check=True)
    return [f"tmp/frame_{ts}.jpg" for ts in timestamps]

def vision_groq(frames):
    from groq import Groq
    client=Groq(api_key=GROQ_API_KEY)
    descs=[]
    for f in frames[:5]: # 5 per request limit
        with open(f,"rb") as img:
            b64=base64.b64encode(img.read()).decode()
        r=client.chat.completions.create(
            model="qwen/qwen3.6-27b",
            messages=[{"role":"user","content":[
                {"type":"text","text":"Describe this TinkerHub maker event frame for documentation. What activity/demo is happening?"},
                {"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}}
            ]}])
        descs.append(r.choices[0].message.content)
    open("tmp/vision.json","w").write(json.dumps(descs, indent=2))
    return descs

def summarize(transcript, visions):
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    model=genai.GenerativeModel("gemini-1.5-flash")
    prompt=f"Create event documentation.\nTranscript:\n{transcript[:8000]}\n\nVisual highlights:\n"+"\n".join(visions)+"\n\nOutput: title, date, summary, key demos, attendees estimate, next steps."
    resp=model.generate_content(prompt)
    open("docs/"+__import__("datetime").datetime.now().strftime("%Y-%m-%d")+".md","w").write(resp.text)
    print(resp.text)
    return resp.text

if __name__=="__main__":
    from config import USE_GEMINI_VIDEO
    if not os.path.exists("tmp/stream.mp4"):
        print("no stream file, waiting for live capture")
    elif USE_GEMINI_VIDEO:
        from pipeline_gemini_video import document_video_gemini
        document_video_gemini("tmp/stream.mp4")
    else:
        extract_audio()
        text=transcribe_groq()
        frames=extract_frames(timestamps=[300,900,1500,2100,2700,3300])
        visions=vision_groq(frames)
        summarize(text, visions)
