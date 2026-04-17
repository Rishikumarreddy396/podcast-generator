# audio_generator.py

from gtts import gTTS
from pydub import AudioSegment
import os
import re
import random
from io import BytesIO
import config # Import config to access the voices list

# --- Define distinct voice pools and pitch shifts ---
# TLDs are grouped based on accent/pitch for variety
MALE_US = ['us']
FEMALE_UK = ['co.uk']
MALE_IN = ['en-IN'] # Special identifier for Indian English
FEMALE_AU = ['com.au'] 
MALE_CA = ['ca']
FEMALE_IE = ['ie']

# Combine all distinct voices for the 'random' cycling pool
ALL_DISTINCT_VOICES = MALE_US + FEMALE_UK + MALE_IN + FEMALE_AU + MALE_CA + FEMALE_IE

# INCREASED PITCH SHIFT for maximum audible difference
MALE_PITCH_SHIFT = -4.5 
FEMALE_PITCH_SHIFT = 4.5

# Map frontend selection values to internal TLD lists
VOICE_POOLS = {
    'random': ALL_DISTINCT_VOICES,
    'male_us': MALE_US,
    'female_uk': FEMALE_UK,
    'male_in': MALE_IN,
    'female_au': FEMALE_AU,
    'female_in': MALE_IN, # NOTE: Using the India TLD as the base for the female_in default
    'male_ca': MALE_CA
}

def create_safe_filename(headline: str) -> str:
    """Cleans a headline to create a valid filename."""
    safe_name = re.sub(r'[\\/*?:"<>|]', "", headline)
    safe_name = safe_name.replace(" ", "_")
    return safe_name[:100] + ".mp3"

def generate_multi_voice_speech(script_parts: list[str], temp_filename: str, selected_voice_key: str = 'random'):
    """
    Generates a single speech file from multiple text parts using different voices,
    and applies pitch modulation based on the voice pool.
    """
    if not script_parts:
        print("No script parts provided for speech generation.")
        return False
        
    print(f"Generating multi-voice speech (Selected Key: {selected_voice_key})...")
    
    combined_audio = AudioSegment.empty()
    
    # Select the appropriate voice pool and shuffle it (on a copy!)
    voices_to_cycle = list(VOICE_POOLS.get(selected_voice_key, ALL_DISTINCT_VOICES))
    
    # Shuffle the list of voices to ensure variety and different starting points
    random.shuffle(voices_to_cycle)
    
    # Ensure there is always a voice to cycle through
    if not voices_to_cycle:
        voices_to_cycle = list(ALL_DISTINCT_VOICES)
        random.shuffle(voices_to_cycle)


    for i, part in enumerate(script_parts):
        try:
            if not part.strip():
                continue
                
            voice_tld = voices_to_cycle[i % len(voices_to_cycle)]
            
            # Determine pitch shift based on the voice key or TLD (heuristic)
            # If the key contains 'female', use female shift. Otherwise, default to male shift.
            if 'female' in selected_voice_key or voice_tld in FEMALE_UK or voice_tld in FEMALE_AU or voice_tld in FEMALE_IE:
                pitch_shift = FEMALE_PITCH_SHIFT
                voice_type = "Higher-Pitched (FEMALE)"
            else:
                pitch_shift = MALE_PITCH_SHIFT
                voice_type = "Lower-Pitched (MALE)"
            
            print(f"  - Generating part {i+1}/{len(script_parts)} with {voice_type} voice '{voice_tld}' (Shift: {pitch_shift})...")
            
            # 1. Generate the base audio segment
            # Special handling for Indian English
            if voice_tld == 'en-IN':
                tts = gTTS(text=part, lang='en', tld='co.in', slow=False)
            else:
                tts = gTTS(text=part, lang='en', tld=voice_tld, slow=False)
            fp = BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            
            audio_segment = AudioSegment.from_mp3(fp)
            
            # 2. Apply the pitch modulation
            new_sample_rate = int(audio_segment.frame_rate * (2.0 ** (pitch_shift / 12.0)))
            
            mod_audio = audio_segment._spawn(audio_segment.raw_data, overrides={'frame_rate': new_sample_rate})
            mod_audio = mod_audio.set_frame_rate(audio_segment.frame_rate)
            
            combined_audio += mod_audio
            
        except Exception as e:
            print(f"    - Error generating audio for part {i+1}: {e}")
            continue

    if len(combined_audio) > 0:
        combined_audio.export(temp_filename, format="mp3")
        print("  - All audio parts combined successfully.")
        return True
    else:
        print("  - Failed to generate any audio segments.")
        return False

def add_background_music(speech_file: str, music_file: str, output_file: str):
    """Mixes a speech file with a background music file."""
    print(f"Mixing audio and saving to {output_file}...")
    try:
        if not os.path.exists(speech_file):
            print(f"Error: Speech file not found at {speech_file}")
            return

        speech = AudioSegment.from_mp3(speech_file)
        
        if os.path.exists(music_file):
            background = AudioSegment.from_mp3(music_file)
            background = background - 12

            if len(background) < len(speech):
                background = background * (len(speech) // len(background) + 1)
            background = background[:len(speech)]

            final_podcast = background.overlay(speech)
        else:
            print("  - Background music file not found. Skipping mixing.")
            final_podcast = speech

        final_podcast.export(output_file, format="mp3")
        print(f"✅ Successfully saved final audio file to {output_file}")
        
    except Exception as e:
        print(f"Error adding background music: {e}")
    finally:
        if os.path.exists(speech_file):
            os.remove(speech_file)