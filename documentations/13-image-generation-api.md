# Image Generation API Specification

This document defines the API contract for the self-hosted image generation service used by Stage 5 of the CURIO content pipeline.

---

## Overview

CURIO's Stage 5 requires a self-hosted image generation API endpoint. The pipeline sends a text prompt and expects a base64-encoded image in response. This allows you to use any image generation model (Stable Diffusion, FLUX, etc.) hosted on your own infrastructure.

---

## API Endpoint

**Environment Variable:** `IMAGE_MODEL_BASE_URL`

**Example:** `http://localhost:5000/generate`

---

## Request Specification

### HTTP Method

```
POST
```

### Headers

```
Content-Type: application/json
```

### Request Body

```json
{
  "prompt": "A cartoon character in a realistic environment",
  "format": "json"
}
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | Yes | The text prompt describing the image to generate |
| `format` | string | Yes | Must be `"json"` for CURIO integration |

---

## Response Specification

### Success Response (200 OK)

```json
{
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
  "seed": 12345,
  "model": "stabilityai/stable-diffusion-xl-base-1.0"
}
```

#### Response Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `image_base64` | string | Yes | Base64-encoded PNG image data |
| `seed` | integer | No | The seed used for generation (useful for reproducibility) |
| `model` | string | No | Identifier of the model used for generation |

### Error Response (4xx/5xx)

```json
{
  "error": "Generation failed: out of memory"
}
```

---

## Reference Implementation

Below is a reference Flask implementation that meets this specification. This example uses Stable Diffusion XL but can be adapted for any model:

```python
"""
app.py - Flask server exposing the image-generation model as an API.
"""

import os
import io
import base64
import random
from flask import Flask, request, jsonify

from diffusers import DiffusionPipeline
import torch

app = Flask(__name__)

CONFIG = {
    "model_id": "stabilityai/stable-diffusion-xl-base-1.0",
    "default_negative_prompt": (
        "blurry, low quality, low resolution, cartoon, illustration, painting, "
        "deformed, disfigured, extra limbs, bad anatomy, watermark, text"
    ),
    "default_width": 1024,
    "default_height": 1024,
    "default_steps": 40,
    "default_guidance_scale": 6.5,
}

STATE = {"pipe": None, "device": None}


def init_model():
    """Load the model at startup."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32
    
    pipe = DiffusionPipeline.from_pretrained(
        CONFIG["model_id"],
        torch_dtype=dtype,
        use_safetensors=True,
    )
    pipe = pipe.to(device)
    
    STATE["pipe"] = pipe
    STATE["device"] = device


@app.route("/generate", methods=["POST"])
def generate():
    if STATE["pipe"] is None:
        return jsonify({"error": "Model not loaded"}), 503

    data = request.get_json()
    prompt = data.get("prompt")
    
    if not prompt:
        return jsonify({"error": "Missing 'prompt'"}), 400

    response_format = data.get("format", "png")

    # Generate image
    result = STATE["pipe"](
        prompt=prompt,
        negative_prompt=CONFIG["default_negative_prompt"],
        width=CONFIG["default_width"],
        height=CONFIG["default_height"],
        num_inference_steps=CONFIG["default_steps"],
        guidance_scale=CONFIG["default_guidance_scale"],
    )
    image = result.images[0]

    # Return base64-encoded image for JSON format
    if response_format == "json":
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        buf.seek(0)
        b64 = base64.b64encode(buf.read()).decode("utf-8")
        return jsonify({
            "image_base64": b64,
            "seed": random.randint(0, 2**31 - 1),
            "model": CONFIG["model_id"]
        })

    return jsonify({"error": "Unsupported format"}), 400


if __name__ == "__main__":
    init_model()
    app.run(host="0.0.0.0", port=5000)
```

---

## Integration with CURIO

Once your API is running, configure CURIO by setting the environment variable:

```bash
export IMAGE_MODEL_BASE_URL="http://your-host:port/generate"
```

CURIO's Stage 5 (`app/stages/stage_5/make_image_from_prompt/bg_image.py`) will:

1. Send a POST request with the generated prompt
2. Expect a JSON response with `image_base64`
3. Decode the base64 data into a PIL Image
4. Pass the image to Stage 6 for text overlay

---

## Hosting Considerations

### GPU Requirements

- **Minimum:** 8GB VRAM for SDXL with optimizations
- **Recommended:** 12GB+ VRAM for stable generation
- **CPU-only:** Possible but very slow (not recommended)

### Performance Optimizations

- Enable attention slicing for lower VRAM usage
- Use model CPU offload if VRAM is limited
- Implement request queuing for concurrent requests
- Add caching for identical prompts

### Security

- Restrict access to CURIO's server IP if possible
- Implement rate limiting
- Validate prompt length to prevent abuse
- Use HTTPS in production

---

## Testing Your API

Test your endpoint with curl:

```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A cat wearing sunglasses", "format": "json"}'
```

Expected response:

```json
{
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
  "seed": 12345,
  "model": "stabilityai/stable-diffusion-xl-base-1.0"
}
```

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| `Model not loaded` | Check GPU availability and model loading logs |
| `Missing 'prompt'` | Ensure request body includes prompt field |
| `Generation failed` | Check VRAM availability, reduce image size/steps |
| `Timeout` | Increase timeout in CURIO or optimize model performance |

### Debug Mode

Enable debug logging in your Flask app to troubleshoot issues:

```python
app.run(host="0.0.0.0", port=5000, debug=True)
```

---

## Alternative Implementations

You can implement this API specification using:

- **FastAPI** for async performance
- **Triton Inference Server** for production deployment
- **vLLM** for optimized LLM/image serving
- **Kubernetes** with GPU node pools for scaling

The only requirement is that your endpoint matches the request/response specification above.

---

## Related Documents

- [Content Pipeline - Stage 5](./04-content-pipeline.md#stage-5---image-generation)
- [Configuration](./09-configuration.md)
- [Architecture](./02-architecture.md)
