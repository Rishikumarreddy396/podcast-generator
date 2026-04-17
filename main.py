# main.py

import schedule
import time
import os
import config
import nltk
from newspaper import Article
from news_fetcher import fetch_latest_articles
from summarizer import prepare_script_from_article
from audio_generator import create_safe_filename, generate_multi_voice_speech, add_background_music

# Ensure NLTK data is downloaded
try:
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)
except Exception as e:
    print(f"Note: Could not download NLTK data: {e}")

processed_article_urls = set()

def process_new_articles():
    """Fetches, processes, and generates categorized, multi-voice audio for new articles."""
    print("--------------------------------------------------")
    articles_from_api = fetch_latest_articles()
    
    # --- NEW DEFAULT VOICE KEY ---
    # Set the default voice key for initial generation
    DEFAULT_VOICE_KEY = 'female_in' 
    # -----------------------------

    for article_data in reversed(articles_from_api):
        url = article_data.get('url')
        title = article_data.get('title')
        category = article_data.get('category', 'general')

        if not all([url, title]):
            continue

        if url not in processed_article_urls:
            print(f"\n✨ New Article Found in '{category}': {title}")

            try:
                print("Downloading full article text...")
                article_parser = Article(url)
                article_parser.download()
                article_parser.parse()
                full_text = article_parser.text

                if not full_text:
                    print("Could not extract full text. Skipping article.")
                    processed_article_urls.add(url)
                    continue

                script_parts = prepare_script_from_article(full_text, title)
                if not script_parts:
                    print("Could not prepare script. Skipping article.")
                    processed_article_urls.add(url)
                    continue

                # --- PATH AND FILENAME SETUP ---
                base_filename = os.path.splitext(create_safe_filename(title))[0]
                
                category_folder = os.path.join(config.OUTPUT_AUDIO_FOLDER, category)
                if not os.path.exists(category_folder):
                    os.makedirs(category_folder)
                
                output_audio_path = os.path.join(category_folder, f"{base_filename}.mp3")
                output_text_path = os.path.join(category_folder, f"{base_filename}.txt") # Path for the transcript
                temp_speech_file = "temp_speech.mp3"

                # --- UPDATED: Pass the DEFAULT_VOICE_KEY ---
                if generate_multi_voice_speech(script_parts, temp_speech_file, selected_voice_key=DEFAULT_VOICE_KEY):
                    add_background_music(temp_speech_file, config.MUSIC_FILE, output_audio_path)
                    
                    # --- SAVE THE TRANSCRIPT ---
                    try:
                        full_script = " ".join(script_parts)
                        with open(output_text_path, 'w', encoding='utf-8') as f:
                            f.write(full_script)
                        print(f"  - Transcript saved to {output_text_path}")
                    except Exception as e:
                        print(f"  - Error saving transcript: {e}")
                    # --------------------------------

                processed_article_urls.add(url)

            except Exception as e:
                print(f"An error occurred while processing article '{title}': {e}")
                processed_article_urls.add(url)

    print("\nWaiting for next check...")


if __name__ == "__main__":
    if not os.path.exists(config.OUTPUT_AUDIO_FOLDER):
        os.makedirs(config.OUTPUT_AUDIO_FOLDER)
        
    print("Starting the real-time news podcast generator.")
    process_new_articles()
    
    schedule.every(config.POLL_INTERVAL_MINUTES).minutes.do(process_new_articles)

    while True:
        schedule.run_pending()
        time.sleep(1)