# app/stages/stage_5/make_image_from_prompt/bg_image.py

"""Generate the post background image from a text prompt via a self-hosted FLUX endpoint."""

import requests
import base64
import io
from PIL import Image
from dotenv import load_dotenv
load_dotenv()
import os

image_model_base_url = os.getenv("IMAGE_MODEL_BASE_URL")  


def meme_image_generate(meme_image_prompt):
    """Render an image from the prompt and return the PIL Image object."""
    try:
        response = requests.post(
            image_model_base_url,
            json={"prompt": f'''{meme_image_prompt} \n\n image must be photorealistic, realistic proportions, natural lighting, '
    'sharp focus, high detail, professional photography''', "format": "json"},
        )
        response.raise_for_status()
        result = response.json()
        image_data = base64.b64decode(result["image_base64"])  # matches app.py's key
        image = Image.open(io.BytesIO(image_data))
        return image

    except Exception as e:
        print(str(e))
        return {"error": str(e)}
    
# meme_image_generate("cat with sunglasses bathing in the bathtub in light bathroom.")