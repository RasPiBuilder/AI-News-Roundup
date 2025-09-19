# AI News Roundup

A simple Python script that fetches the latest AI and tech news from selected sites, summarizes the results, and generates both a text and spoken narration roundup.

This project is intended as a **demo of workflow and processes**, not a production tool.

---

## Features
- 🔎 **Search**: Queries news snippets from DuckDuckGo (`ddgs`) with topic + site modifiers.  
- 📝 **Summarization**: Uses `sumy`’s LSA summarizer to condense snippets into short summaries.  
- 📢 **Narration**: Builds a human-readable script with topic transitions.  
- 🎙️ **Text-to-Speech**: Uses `pyttsx3` to generate a `.wav` audio narration file.  

---

## Example Workflow
1. Define topics, news sites, and search modifiers in the config section.  
2. Script randomly combines them into search queries.  
3. For each topic:
   - Retrieves news snippets  
   - Summarizes them  
   - Prints/logs the results  
4. Builds a narration that strings together all summaries.  
5. Saves both `narration.txt` and `narration.wav`.  

---

## Requirements
Install the dependencies:
```bash
pip install ddgs sumy pyttsx3
```

---

## Usage
Run the script directly:
```bash
python ai_news_roundup.py
```

The script will:
- Print search results and summaries to the terminal  
- Write a narration file (`narration.txt`)  
- Generate spoken narration (`narration.wav`)  

---

## Additional / Coming Soon
Planned extensions for this demo include:
- 🎬 Automatic generation of **video clips** from the narration  
- 📊 Enhanced topic configuration and customization  
- 🌐 Multi-language support  

---

## Notes
- This is a **demo project** showcasing a workflow combining search, summarization, and speech synthesis.  
- Results depend on the search engine and may vary from run to run.  
- Config values (topics, sites, modifiers) can be easily extended or customized.  

---

## License
MIT License
