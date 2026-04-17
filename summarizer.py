# summarizer.py

import config
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch

# Initialize the summarization model and tokenizer once when the module is loaded
print("Loading summarization model...")
model_name = "facebook/bart-large-cnn"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
print("Summarization model loaded.")

def prepare_script_from_article(article_content: str, title: str) -> list[str]:
    """
    Summarizes article content and formats it into a list of script parts
    for multi-voice generation.
    """
    if not article_content:
        return []

    print(f"Summarizing article: {title}")
    
    try:
        # Manually perform summarization using the model and tokenizer
        inputs = tokenizer([article_content], max_length=1024, return_tensors="pt", truncation=True)
        summary_ids = model.generate(
            inputs["input_ids"], 
            num_beams=4, 
            max_length=250, 
            min_length=100, 
            early_stopping=True,
            do_sample=False
        )
        summary_text = tokenizer.decode(summary_ids[0], skip_special_tokens=True, clean_up_tokenization_spaces=False)

        # Format into distinct parts for different voices
        script_parts = [
            f"Our next story is titled: {title}.",
            summary_text,
            "And that concludes this report."
        ]
        
        return script_parts

    except Exception as e:
        print(f"Error during summarization: {e}")
        # Fallback to simple truncation if summarization fails
        words = article_content.split()
        script_words = words[:config.TARGET_WORD_COUNT]
        fallback_text = " ".join(script_words)
        return [f"The next story is: {title}.", fallback_text]