# ai_news_roundup.py

# --- Core Python ---
import os
import random
import requests
import re
from datetime import datetime

# --- Third-party ---
from ddgs import DDGS  # DuckDuckGo search
from groq import Groq  # Groq LPU API
import pyttsx3
from pptx import Presentation
from pptx.util import Inches, Pt
from PIL import Image, UnidentifiedImageError  # for image validation

# ---------------- CONFIG ---------------- #

TOPICS = {
    "Anthropic": ["Anthropic news", "Claude AI updates", "Anthropic announcements"],
    "OpenAI": ["OpenAI news", "OpenAI announcements", "GPT-5 updates", "ChatGPT news"],
    "Humanoid Robots": ["humanoid robot news", "robotics breakthroughs", "AI-powered robots"],
    "AI Startups": ["AI startup venture capital", "AI funding news", "AI startup acquisitions"]
}

SITES = [
    "theverge.com",
    "arstechnica.com",
    "techcrunch.com",
    "the-decoder.com",
    "sciencedaily.com"
]

SEARCH_MODIFIERS = [
    "September 2025",
    "latest",
    "breaking",
    "update",
    "research"
]

OUTPUT_DIR = "output"
AUDIO_DIR = os.path.join(OUTPUT_DIR, "audio_clips")
IMAGE_DIR = os.path.join(OUTPUT_DIR, "images")
PPTX_FILE = os.path.join(OUTPUT_DIR, "news_roundup.pptx")

# Ensure dirs exist
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)

# ---------------- GROQ SETUP ---------------- #
GROQ_API_KEY = "YOUR-API-KEY-HERE"  # replace with env var in production
client = Groq(api_key=GROQ_API_KEY)

def groq_call(prompt, max_tokens=300):
    """Helper to call Groq API and return text restricted to the requested format only."""
    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a precise formatter. Respond in the exact format requested. "
                    "Do NOT include explanations, headings, labels, prefaces, or markdown fences. "
                    "Output ONLY the content asked for."
                )
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_completion_tokens=max_tokens
    )
    return response.choices[0].message.content.strip()

# ---------------- CORE FUNCTIONS ---------------- #

def search_snippets(query, num_results=5):
    """Fetch snippets for a given search term using DuckDuckGo"""
    snippets = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=num_results):
            title = r.get("title", "").strip()
            body = r.get("body", "").strip()
            if title or body:
                snippets.append(f"{title}: {body}".strip(": "))
    return snippets

def get_bullet_points(summary):
    """Use Groq to turn summary into 5-7 concise bullet points (one per line, nothing else)"""
    prompt = (
        "Turn the following news summary into 5–7 concise bullet points.\n"
        "Formatting requirements:\n"
        "- Output ONLY the bullet lines, one per line.\n"
        "- No numbering, no dashes or bullet symbols, no intro/outro text, no headings.\n"
        "- Keep each line under 18 words if possible.\n\n"
        f"{summary}"
    )
    return groq_call(prompt)

def get_script(summary, bullets):
    """Use Groq to generate a short narration script (approx 2–3 minutes)"""
    prompt = (
        "Write a natural, conversational narration covering the topic using the material below.\n"
        "Length target: ~220–350 words.\n"
        "Formatting requirements:\n"
        "- Output ONLY the narration text (plain paragraphs). No titles, labels, or extra commentary.\n"
        "- Do not restate requirements.\n\n"
        f"SUMMARY:\n{summary}\n\n"
        f"BULLETS:\n{bullets}"
    )
    return groq_call(prompt, max_tokens=600)

def get_image_keywords(summary):
    """Ask Groq to suggest 1–2 short search keywords for images"""
    prompt = (
        "From the summary below, output 1–2 short keyword phrases for an image search.\n"
        "Formatting requirements:\n"
        "- Output ONLY the keywords, separated by a comma if there are two.\n"
        "- No quotes, no labels, no extra text.\n\n"
        f"{summary}"
    )
    return groq_call(prompt, max_tokens=30)

def _sanitize_keywords(keywords_text):
    """Normalize keyword text into a short comma-separated string suitable for search."""
    parts = [p.strip("•-–— \t\"'`") for p in re.split(r"[,\n;/]+", keywords_text) if p.strip()]
    # Keep at most 2 phrases, join with comma
    return ", ".join(parts[:2]) if parts else ""

def validate_image_file(img_path, min_size=100):
    """Return True if the path points to a real, decodable image of a reasonable size."""
    try:
        with Image.open(img_path) as im:
            im.verify()  # quick integrity check
        with Image.open(img_path) as im:
            im.load()   # make sure it can fully load
            w, h = im.size
        return w >= min_size and h >= min_size
    except (UnidentifiedImageError, OSError, ValueError):
        return False

def fetch_image(keywords, filename):
    """Download a valid image result from DuckDuckGo; verify it decodes and has reasonable dimensions."""
    img_path = os.path.join(IMAGE_DIR, filename)
    kw = _sanitize_keywords(keywords)
    if not kw:
        return None

    with DDGS() as ddgs:
        # Try several results until one validates
        for r in ddgs.images(kw, max_results=5):
            url = r.get("image") or r.get("thumbnail")
            if not url:
                continue
            try:
                resp = requests.get(url, timeout=10)
                if resp.status_code != 200:
                    continue
                ctype = resp.headers.get("Content-Type", "")
                if "image" not in ctype.lower():
                    continue
                with open(img_path, "wb") as f:
                    f.write(resp.content)
                if validate_image_file(img_path):
                    return img_path
                else:
                    try:
                        os.remove(img_path)
                    except OSError:
                        pass
            except Exception:
                # try the next candidate
                continue
    return None

def save_audio(text, filename):
    """Convert narration text to speech and save to file"""
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    for v in voices:
        if "Zira" in v.name:
            engine.setProperty("voice", v.id)
            break
    engine.setProperty("rate", 175)
    engine.setProperty("volume", 0.9)
    engine.save_to_file(text, filename)
    engine.runAndWait()
    print(f"🎙 Queued audio: {filename}")

def get_intro_text(date_str, topics):
    """Generate a concise intro narration."""
    topic_list = ", ".join(topics)
    prompt = (
        f"Write a concise intro (2–3 sentences, ~15–25 seconds) for an AI & tech news roundup dated {date_str}. "
        f"Casually mention the topics: {topic_list}. "
        "Formatting requirements:\n"
        "- Output ONLY the intro narration (plain text). No title, no labels."
    )
    return groq_call(prompt, max_tokens=160)

def get_outro_text():
    """Generate a concise outro narration."""
    prompt = (
        "Write a concise outro (1–2 sentences, ~10–20 seconds) that thanks the audience and invites them back tomorrow. "
        "Formatting requirements:\n"
        "- Output ONLY the outro narration (plain text). No title, no labels."
    )
    return groq_call(prompt, max_tokens=120)

def build_ppt(segments):
    """Build a PowerPoint with intro, topic slides (with image + bullets), outro"""
    prs = Presentation()
    title_slide_layout = prs.slide_layouts[0]
    bullet_slide_layout = prs.slide_layouts[1]

    # Intro
    slide = prs.slides.add_slide(title_slide_layout)
    title, subtitle = slide.shapes.title, slide.placeholders[1]
    title.text = "AI & Tech News Roundup"
    subtitle.text = datetime.now().strftime("%B %d, %Y")

    # Topics
    for seg in segments:
        slide = prs.slides.add_slide(bullet_slide_layout)
        title_shape, content_shape = slide.shapes.title, slide.placeholders[1]
        title_shape.text = seg["topic"]

        # --- Text area (left side) ---
        tf = content_shape.text_frame
        tf.clear()
        for line in seg["bullets"].splitlines():
            if line.strip():
                p = tf.add_paragraph()
                p.text = line.strip()
                p.font.size = Pt(18)

        # Resize/move text box to left half
        content_shape.left = Inches(0.5)
        content_shape.top = Inches(1.5)
        content_shape.width = Inches(5)
        content_shape.height = Inches(5)

        # --- Image area (right side) ---
        if seg.get("image"):
            try:
                slide.shapes.add_picture(
                    seg["image"],
                    Inches(5.7),   # right half
                    Inches(1.5),
                    width=Inches(4),
                    height=Inches(3.5)
                )
            except Exception:
                pass

    # Outro
    slide = prs.slides.add_slide(title_slide_layout)
    title, subtitle = slide.shapes.title, slide.placeholders[1]
    title.text = "Thanks for Watching"
    subtitle.text = "Stay tuned for tomorrow's update!"

    prs.save(PPTX_FILE)
    print(f"✅ Saved presentation: {PPTX_FILE}")

# ---------------- MAIN EXECUTION ---------------- #

if __name__ == "__main__":
    today = datetime.now().strftime("%A, %B %d, %Y")
    print(f"\n📅 Fetching news for {today}\n")

    all_segments = []
    clip_num = 1

    for topic, base_terms in TOPICS.items():
        chosen_base = random.choice(base_terms)
        chosen_sites = random.sample(SITES, k=min(2, len(SITES)))
        site_summaries = []

        print(f"\n🔎 Topic: {topic}")

        for site in chosen_sites:
            modifier = random.choice(SEARCH_MODIFIERS)
            query = f"{chosen_base} {modifier} site:{site}"
            print(f"   Searching: {query}")

            snippets = search_snippets(query)
            if not snippets:
                continue
            combined = " ".join(snippets[:5])
            site_summaries.append(f"{site}: {combined[:400]}")

        if not site_summaries:
            continue

        # Merge into one raw summary
        raw_summary = " ".join(site_summaries)

        # Generate bullets, script, image
        bullets = get_bullet_points(raw_summary)
        script = get_script(raw_summary, bullets)
        keywords = get_image_keywords(raw_summary)
        img_file = fetch_image(keywords, f"{topic.replace(' ', '_')}.jpg")

        # Save audio (topic clip)
        audio_file = os.path.join(AUDIO_DIR, f"clip_{clip_num:02}.wav")
        save_audio(script, audio_file)
        clip_num += 1

        all_segments.append({
            "topic": topic,
            "bullets": bullets,
            "script": script,
            "audio": audio_file,
            "image": img_file
        })

    # Intro/Outro audio generation
    topics_covered = [seg["topic"] for seg in all_segments]
    intro_text = get_intro_text(datetime.now().strftime("%B %d, %Y"), topics_covered) if topics_covered else \
        f"Welcome to your AI and tech news roundup for {datetime.now().strftime('%B %d, %Y')}."
    outro_text = get_outro_text()

    intro_audio = os.path.join(AUDIO_DIR, "intro.wav")
    outro_audio = os.path.join(AUDIO_DIR, "outro.wav")
    save_audio(intro_text, intro_audio)
    save_audio(outro_text, outro_audio)

    print(f"✅ Saved {clip_num-1} topic audio clips + 2 intro/outro clips to {AUDIO_DIR}")
    build_ppt(all_segments)

