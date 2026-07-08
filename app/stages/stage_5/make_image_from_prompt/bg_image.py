# app/stages/stage_5/make_image_from_prompt/bg_image.py

"""Generate the post background image from a text prompt via Hugging Face."""

from dotenv import load_dotenv
load_dotenv()
import os
hf_token = os.getenv("HF_TOKEN")

import time


from huggingface_hub import InferenceClient

def meme_image_generate(meme_image_prompt):
    """Render an image from the prompt and return its numeric file identifier."""
    error = {'error': None}

    try:
        id = int(time.time())
        
        client = InferenceClient(token=hf_token) 

        image = client.text_to_image(
            meme_image_prompt,
            model="black-forest-labs/FLUX.1-schnell",
        )

        return image
    
    except Exception as e:
        error['error'] = str(e)
        print(str(e))
        return error