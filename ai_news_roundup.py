# ai_news_roundup.py
from ddgs import DDGS
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from datetime import datetime
import pyttsx3
import random


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


def summarize_text(snippets, sentence_count=3):
    """Summarize snippets into a clean short paragraph"""
    if not snippets:
        return "No reliable information found."
    combined = " ".join(snippets)
    parser = PlaintextParser.from_string(combined, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary_sentences = summarizer(parser.document, sentence_count)
    summary = " ".join(str(s) for s in summary_sentences)
    return summary.strip()


def build_narration(topic_summaries):
    """Combine all summaries into a narration script with transitions"""
    today = datetime.now().strftime("%A, %B %d, %Y")
    narration = [f"Here are the top Tech and AI stories for today, {today}.\n"]

    transitions = ["Meanwhile,", "On another note,", "Also trending,", "Finally,"]

    for i, (topic, site_summaries) in enumerate(topic_summaries.items(), start=1):
        if i == 1:
            narration.append(f"Story {i}: {topic}")
        else:
            transition = random.choice(transitions)
            narration.append(f"{transition} story {i}: {topic}")

        for site, summary in site_summaries.items():
            narration.append(f"- {site}: {summary}")

        narration.append("")

    narration.append("That wraps up today’s roundup. Stay tuned for more tomorrow!")
    return "\n".join(narration)


def speak_narration(text, filename="narration.wav"):
    """Convert narration text to speech and save to file"""
    engine = pyttsx3.init()

    voices = engine.getProperty("voices")
    for v in voices:
        if "Zira" in v.name:
            engine.setProperty("voice", v.id)
            print(f"✅ Using voice: {v.name}")
            break

    engine.setProperty("rate", 180)
    engine.setProperty("volume", 0.9)

    engine.save_to_file(text, filename)
    engine.runAndWait()
    print(f"✅ Saved narration to {filename}")


# ---------------- MAIN EXECUTION ---------------- #

if __name__ == "__main__":
    today = datetime.now().strftime("%A, %B %d, %Y")
    print(f"\n📅 Fetching news for {today}")

    topic_summaries = {}

    for topic, base_terms in TOPICS.items():
        chosen_base = random.choice(base_terms)
        chosen_sites = random.sample(SITES, k=min(2, len(SITES)))  # pick 2 sites randomly
        site_summaries = {}

        print(f"\n🔎 Topic: {topic}")

        for site in chosen_sites:
            modifier = random.choice(SEARCH_MODIFIERS)
            query = f"{chosen_base} {modifier} site:{site}"
            print(f"   Searching: {query}")

            snippets = search_snippets(query)
            for s in snippets:
                print("   -", s)

            summary = summarize_text(snippets, sentence_count=3)
            site_summaries[site] = summary

            print(f"   ✍️ Summary ({site}): {summary}")
            print("   " + "-" * 60)

        topic_summaries[topic] = site_summaries

    narration_text = build_narration(topic_summaries)

    print("\n\n📢 Final Narration:\n")
    print(narration_text)

    with open("narration.txt", "w", encoding="utf-8") as f:
        f.write(narration_text)

    speak_narration(narration_text, "narration.wav")

