# 🎙️ News Podcast Generator

An automated system that fetches daily news, summarizes the content using AI, and converts it into high-quality audio podcasts with multiple voices and background music.

## 🌟 Features

*   **Real-time News Fetching:** Uses [NewsAPI](https://newsapi.org/) to get the latest headlines across multiple categories (Tech, Business, Sports, etc.).
*   **AI-Powered Summarization:** Automatically summarizes long articles into concise scripts using the **BART Large CNN** model from Hugging Face.
*   **Multi-Voice Audio:** Generates speech using different accents and pitch shifts to create a "broadcast" feel.
*   **Background Music Mixing:** Layers generated speech over background music for a professional listening experience.
*   **Interactive Web Dashboard:** A Flask-based interface to browse, listen to, and even regenerate podcasts with different voice profiles.

---

## 🏗️ Architecture

The project consists of two primary components:

1.  **Background Worker (`main.py`):** The "Producer" that polls NewsAPI, processes articles, and saves them as audio and transcript files.
2.  **Web Server (`server.py`):** The "Consumer" that provides a UI to browse the generated podcast library and allows for on-demand audio regeneration.

---

## 🚀 Getting Started

### Prerequisites

*   **Python 3.8+**
*   **FFmpeg:** Required for audio processing (`pydub`).
    *   *Windows:* Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH.
    *   *macOS:* `brew install ffmpeg`
    *   *Linux:* `sudo apt install ffmpeg`

### 1. Installation

Clone the repository and install the Python dependencies:

```bash
git clone https://github.com/your-username/news-podcast.git
cd news-podcast
pip install -r requirements.txt
```

### 2. Configuration

Open `config.py` to customize the system:
*   **`NEWS_API_KEY`**: Replace with your own key from [NewsAPI.org](https://newsapi.org/).
*   **`CATEGORIES`**: Modify the list of news categories you want to follow.
*   **`POLL_INTERVAL_MINUTES`**: Adjust how frequently the background worker checks for new articles.

### 3. Running the Project

You need to run **two** separate processes:

#### A. Start the Background Worker
This process will fetch news and generate the podcasts.
```bash
python main.py
```
*Note: On the first run, it will download the BART model (~1.6GB). This might take a few minutes.*

#### B. Start the Web Dashboard
In a new terminal window, start the UI:
```bash
python server.py
```
Open your browser and navigate to **`http://localhost:5001`**.

---

## 📁 Project Structure

*   `main.py`: Entry point for the background news processing worker.
*   `server.py`: Flask web server providing the API and dashboard.
*   `news_fetcher.py`: Logic for interacting with NewsAPI.
*   `summarizer.py`: NLP logic using Transformers for article summarization.
*   `audio_generator.py`: TTS logic (gTTS) and audio mixing (pydub).
*   `config.py`: Centralized configuration and settings.
*   `generated_podcasts/`: Storage for generated audio and transcripts (ignored by git).
*   `static/` & `templates/`: Frontend assets for the web dashboard.

---

## 🛠️ Tech Stack

*   **Language:** Python
*   **Framework:** Flask
*   **AI/NLP:** Hugging Face Transformers (BART model), newspaper3k
*   **Audio:** gTTS, pydub
*   **Task Scheduling:** schedule
