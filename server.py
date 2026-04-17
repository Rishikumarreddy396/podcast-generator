# server.py

import os
import re
from flask import Flask, jsonify, send_from_directory, request, render_template
# Import necessary functions for regeneration
from audio_generator import generate_multi_voice_speech, add_background_music 
import config # Needed to access MUSIC_FILE path

# --- Configuration ---
project_root = os.path.abspath(os.path.dirname(__file__))
OUTPUT_FOLDER = os.path.join(project_root, 'generated_podcasts')

# --- Flask App Initialization ---
app = Flask(__name__)

# --- Route to serve the main HTML page ---
@app.route('/')
def serve_index():
    return render_template('index.html')

# --- API Endpoint to get the list of categorized podcasts (Unchanged) ---
@app.route('/api/podcasts')
def list_podcasts():
    categorized_podcasts = {}
    if not os.path.exists(OUTPUT_FOLDER):
        return jsonify({})

    try:
        for category_name in sorted(os.listdir(OUTPUT_FOLDER)):
            category_path = os.path.join(OUTPUT_FOLDER, category_name)
            if os.path.isdir(category_path):
                podcasts_in_category = []
                for filename in sorted(os.listdir(category_path), reverse=True):
                    if filename.endswith('.mp3'):
                        title = filename.replace('.mp3', '').replace('_', ' ')
                        podcasts_in_category.append({
                            "title": title,
                            "filename": filename,
                            "category": category_name
                        })
                if podcasts_in_category:
                    categorized_podcasts[category_name] = podcasts_in_category
        
        return jsonify(categorized_podcasts)
    except Exception as e:
        print(f"Error listing podcasts: {e}")
        return jsonify({"error": "Could not read podcast directory"}), 500

# --- Route to serve the audio files (Unchanged) ---
@app.route('/podcasts/<category>/<path:filename>')
def serve_podcast(category, filename):
    category_path = os.path.join(OUTPUT_FOLDER, category)
    return send_from_directory(category_path, filename)

# --- API Endpoint to serve the transcript text file (Unchanged) ---
@app.route('/api/transcript/<category>/<filename>')
def serve_transcript(category, filename):
    """Serves the content of a transcript .txt file."""
    try:
        base_filename = os.path.splitext(filename)[0]
        text_filename = f"{base_filename}.txt"
        category_path = os.path.join(OUTPUT_FOLDER, category)
        
        if not os.path.exists(os.path.join(category_path, text_filename)):
            return jsonify({"error": "Transcript not found"}), 404
            
        with open(os.path.join(category_path, text_filename), 'r', encoding='utf-8') as f:
            content = f.read()
        return jsonify({"transcript": content})

    except Exception as e:
        print(f"Error serving transcript: {e}")
        return jsonify({"error": "Could not read transcript file"}), 500

# --- NEW: Regeneration Endpoint ---
@app.route('/api/regenerate_podcast', methods=['POST'])
def regenerate_podcast():
    """Reads the existing script and regenerates the audio with a new voice."""
    data = request.get_json()
    category = data.get('category')
    filename_mp3 = data.get('filename')
    new_voice_key = data.get('voice_key')

    if not all([category, filename_mp3, new_voice_key]):
        return jsonify({"error": "Missing parameters."}), 400

    try:
        # 1. Define paths and check file existence
        base_filename = os.path.splitext(filename_mp3)[0]
        category_folder = os.path.join(OUTPUT_FOLDER, category)
        output_audio_path = os.path.join(category_folder, filename_mp3)
        input_text_path = os.path.join(category_folder, f"{base_filename}.txt")
        temp_speech_file = f"temp_regenerate_{base_filename}.mp3"

        if not os.path.exists(input_text_path):
            return jsonify({"error": "Original script not found (missing .txt file). Run main.py first."}), 404

        # 2. Read the existing script from the transcript file
        with open(input_text_path, 'r', encoding='utf-8') as f:
            full_script = f.read()
        
        # 3. Split the full script back into parts for the multi-voice generator
        # The script was joined by ' '. We split by sentence endings for voice separation.
        # This is a robust way to recreate the speaking parts.
        script_parts = re.split(r'(?<=[.?!])\s+', full_script.strip())
        
        # 4. Regenerate the audio with the new voice key
        if generate_multi_voice_speech(script_parts, temp_speech_file, selected_voice_key=new_voice_key):
            # 5. Mix with background music (accessing music file from config)
            add_background_music(temp_speech_file, config.MUSIC_FILE, output_audio_path)
            
            return jsonify({
                "success": True, 
                "message": f"Podcast regenerated with {new_voice_key}.", 
                "new_audio_url": f"/podcasts/{category}/{filename_mp3}"
            })
        
        return jsonify({"error": "Failed to generate new audio."}), 500

    except Exception as e:
        print(f"Error during podcast regeneration: {e}")
        return jsonify({"error": f"Internal server error: {e}"}), 500

# --- Main execution ---
if __name__ == '__main__':
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
    app.run(host='0.0.0.0', port=5001, debug=True)