# AI News Roundup

A Python script that fetches the latest AI and tech news from selected sites, summarizes the results with an LLM, and generates a narrated slideshow (PowerPoint) with both text and audio clips.  

This project is intended as a **demo of workflow and process automation**, not a production tool.  

---

## ✨ Features

- 🔎 **Search**: Queries news snippets from DuckDuckGo (via `ddgs`) with topic, site, and modifier combinations.  
- 📝 **Summarization & Formatting**: Uses **Groq’s LPU API** (Meta LLaMA model) to generate:  
  - Concise bullet points (5–7 per topic).  
  - A narration script (~2–3 minutes, conversational).  
  - Short image search keywords.  
- 🖼️ **Image Retrieval**: Downloads and validates images (DuckDuckGo image search + Pillow validation).  
- 🎙️ **Text-to-Speech**: Uses `pyttsx3` to create `.wav` audio narration files for:  
  - **Intro**  
  - **Each topic**  
  - **Outro**  
- 📊 **PowerPoint Generation**: Builds a `.pptx` slideshow with:  
  - Title slide (date-stamped)  
  - One slide per topic (bullets + image)  
  - Outro slide  

---

## ⚙️ Example Workflow

1. Define topics, news sites, and search modifiers in the **config section**.  
2. The script randomly combines them into queries.  
3. For each topic:  
   - Retrieves recent news snippets.  
   - Summarizes them into bullets and a narration script.  
   - Extracts image keywords and validates downloaded images.  
   - Saves narration as audio.  
4. Generates **intro** and **outro** narration + audio.  
5. Builds a PowerPoint presentation with all content.  

Outputs:  
- `output/audio_clips/` → `.wav` narration files (intro, per-topic, outro)  
- `output/images/` → downloaded/validated images  
- `output/news_roundup.pptx` → narrated news roundup slideshow  

---

## 📦 Requirements

Install dependencies:  

```bash
pip install ddgs groq pyttsx3 python-pptx pillow requests
```

---

## ▶️ Usage

Run the script directly:  

```bash
python news_roundup.py
```

The script will:  
- Print progress in the terminal.  
- Save `.wav` audio clips for intro, each topic, and outro.  
- Save topic images.  
- Build a PowerPoint file (`news_roundup.pptx`) in the `output/` directory.  

---

## 🚧 Notes & Limitations

- This is a **demo project** showing how to combine search, summarization, TTS, and slide generation.  
- Results depend on search engine responses and may vary per run.  
- Groq API key must be set in the script (currently hardcoded, should be swapped to env var for production).  
- Audio voice uses `pyttsx3` defaults (customization depends on available system voices).  

---

## 📜 License

MIT License  

- Config values (topics, sites, modifiers) can be easily extended or customized.  

---

## License
MIT License
