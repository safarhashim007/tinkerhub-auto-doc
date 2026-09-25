# Router: Gemini for major events, hybrid small for daily
EVENT_CONFIG={
 "ai_wednesday": {"audio_weight":0.7, "video_weight":0.3, "model":"groq_hybrid"}, # more audio
 "maker_thursday": {"audio_weight":0.3, "video_weight":0.7, "model":"groq_hybrid"}, # more video
 "security_tuesday": {"audio_weight":0.5, "video_weight":0.5, "model":"groq_hybrid"},
 "major": {"model":"gemini"} # major -> full Gemini 1.5hr digest
}
def route(event_name):
    n=event_name.lower()
    if "major" in n or "hackathon" in n or "summit" in n: return EVENT_CONFIG["major"]
    if "maker" in n: return EVENT_CONFIG["maker_thursday"]
    if "ai" in n: return EVENT_CONFIG["ai_wednesday"]
    return EVENT_CONFIG["security_tuesday"]
