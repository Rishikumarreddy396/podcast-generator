# config.py

# --- API Settings ---
NEWS_API_KEY = "64a309fa56974ddabe9107b2c649e533" # Replace with your own key if needed
# Define the country and categories to fetch news from.
# Note: You cannot mix 'sources' with the 'country' or 'category' parameters in the NewsAPI.
NEWS_COUNTRY = "us" 
CATEGORIES = ["technology", "sports", "business", "science", "health", "entertainment"]

# --- Audio Settings ---
OUTPUT_AUDIO_FOLDER = "generated_podcasts" 
MUSIC_FILE = "background.mp3"
# A list of gTTS top-level domains to simulate different voices/accents
TTS_VOICES = ['com.au', 'co.uk', 'us', 'ca', 'co.in', 'ie', 'co.za']

# --- Script Generation Settings ---
# Words per minute for the TTS voice (average is ~150)
WORDS_PER_MINUTE = 150
# Desired audio length in minutes (e.g., 4 minutes)
TARGET_AUDIO_MINUTES = 4
# Calculate the target word count
TARGET_WORD_COUNT = WORDS_PER_MINUTE * TARGET_AUDIO_MINUTES

# --- Scheduler Settings ---
# How often to check for new articles, in minutes
POLL_INTERVAL_MINUTES = 15