# 🕰️ AI Time Capsule & Trend Oracle

An AI-powered RAG (Retrieval-Augmented Generation) application that lets you travel back to any month between 2015 and 2026 and ask questions — the AI answers using ONLY real data from that exact time period.

## 🌟 What Makes This Unique

Most AI chatbots answer from general knowledge, which means they can accidentally mix up timelines or hallucinate. This app **physically locks the AI out of the future** using metadata filtering on a vector database — it can only see real news, world events, and music charts from the month you selected.

## 🚀 Live Demo
[Coming soon — Streamlit Cloud link]

## 🛠️ Tech Stack

| Component | Tool Used |
|---|---|
| Vector Database | ChromaDB |
| Embeddings | all-MiniLM-L6-v2 (via ChromaDB) |
| Text Splitting | Custom character splitter with overlap |
| Metadata Filtering | ChromaDB `where` filter (the time-lock) |
| Generation | Google Gemini 2.5 Flash |
| Frontend | Streamlit |
| News Data | NYT Archive API |
| World Events | Wikipedia Current Events |
| Music Charts | Billboard Hot 100 (1958–2026) |

## 📦 Project Structure
AI-Time-Capsule/
app/                          # Streamlit frontend
data_collection/              # Scripts to fetch NYT + Wikipedia data
data_processing/              # Chunking + tagging pipeline
embeddings/                   # Vector DB build + search
generation/                   # Gemini answer generation
requirements.txt

## ⚙️ How It Works

1. **Data Collection** — NYT Archive API + Wikipedia Current Events scraped month by month (2015–2026), combined with Billboard Hot 100 historical chart data
2. **Text Splitting** — Long chunks broken into 500-character pieces with 50-character overlap so no context is lost at boundaries
3. **Embedding + Storage** — Every chunk embedded and stored in ChromaDB with a `year_month` metadata tag
4. **Date Locking** — When you pick a month, ChromaDB's `where` filter restricts search to only that month's chunks before similarity search runs — the AI never sees anything outside your chosen window
5. **Generation** — Retrieved chunks passed to Gemini with a strict prompt: "answer using ONLY this information"
6. **Honest fallback** — If no relevant chunks are found (e.g. cricket, regional sports), the app shows a clear warning instead of hallucinating an answer

## 🗂️ Data Coverage

- **138 months** of data (January 2015 – June 2026)
- **720,155 chunks** stored in the vector database
- Sources: NYT (news), Wikipedia Current Events (world events), Billboard Hot 100 (music)

## 🔍 Two Modes

- **🕰️ Time Travel** — Pick a specific month, ask anything about that era
- **🌍 Free Ask** — Ask without a date filter, searches across all years

## 💡 Example Questions

- "What song was everyone listening to?" → July 2016
- "What is happening in the world right now?" → March 2020
- "Who won the US election?" → November 2024
- "What were the biggest news stories?" → February 2022

## 🚀 Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Set your API keys
export GEMINI_API_KEY="your_key"
export NYT_API_KEY="your_key"

# Fetch data (one-time)
python data_collection/fetch_many_months.py 2015 1 2026 6

# Build chunks
python data_processing/chunk_and_tag.py

# Build vector database
python embeddings/build_vector_db.py

# Run the app
streamlit run app/streamlit_app.py
```

## ⚠️ Data Limitations

This app works best for:
- Major world news and politics
- Music charts and pop culture
- COVID-related events (2020–2021)
- US and global elections

Coverage is limited for: cricket, regional Indian sports, Bollywood, and local news (sources are NYT and Wikipedia, which skew toward global/US coverage).

## 👩‍💻 Built By

Tripti Yadav — M.Sc. Statistics, Ramniranjan Jhunjhunwala College, Mumbai

[GitHub](https://github.com/TriptiYadav31) | [LinkedIn](https://www.linkedin.com/in/tripti-yadav-20a871305)
