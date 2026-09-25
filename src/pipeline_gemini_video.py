import os, time
from config import GEMINI_API_KEY

def document_video_gemini(video_path="tmp/stream.mp4"):
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=GEMINI_API_KEY)
    print(f"uploading {video_path} to Gemini File API (AQ. key, 1.5hr digest)...")
    f = client.files.upload(file=video_path)
    while f.state.name == "PROCESSING":
        print("processing video...")
        time.sleep(10)
        f = client.files.get(name=f.name)
    if f.state.name != "ACTIVE":
        raise RuntimeError(f"Gemini file failed: {f.state.name}")
    prompt = """You are documenting a TinkerHub event VERY DETAILED.
Extract HOST NAME from intro/slides/speech.
Watch full 1.5hr video and output markdown:
# Title
Date, Duration, Host: <name>, Event type
## Detailed Summary (10-12 lines)
## Timeline with timestamps [mm:ss] - every major segment
## Demos/Projects shown in detail
## Tools / tech / code mentioned
## Host & speakers
## Audience Q&A
## Key takeaways & Next steps
Include host name prominently."""
    resp = client.models.generate_content(model="gemini-2.5-flash", contents=[f, prompt])
    out = f"docs/{__import__('datetime').datetime.now().strftime('%Y-%m-%d')}-gemini.md"
    os.makedirs("docs", exist_ok=True)
    open(out,"w").write(resp.text)
    print(f"documented to {out}")
    print(resp.text[:2000])
    return resp.text

if __name__=="__main__":
    if os.path.exists("tmp/stream.mp4"):
        document_video_gemini()
    elif os.path.exists("tmp/test_ai_wednesday.mp4"):
        document_video_gemini("tmp/test_ai_wednesday.mp4")
    else:
        print("no tmp/stream.mp4 - place 1.5hr mp4 there to test")
