import requests
import io
import base64
from config import cloudflare_ai_token

if cloudflare_ai_token == "YOUR_API_TOKEN":
    raise Exception("Replace `YOUR_API_TOKEN` with your Gemini API token in `config.py`")

API_BASE_URL = "https://api.cloudflare.com/client/v4/accounts/9bdeb8e5e08bcad2bd69c33cc2ba15ae/ai/run/"
headers = {"Authorization": f"Bearer {cloudflare_ai_token}"}

paintSchema = {'function_declarations': [
    {'name': 'paint',
     'description': """Paint a picture.""",
     'parameters': {'type_': 'OBJECT',
                    'properties': {
                        'keywords': {'type_': 'STRING',
                                     'description': "Keywords to paint."}
                    },
                    'required': ['keywords']}}]}


def paint(keywords):
    response = requests.post(f"{API_BASE_URL}@cf/bytedance/stable-diffusion-xl-lightning", headers=headers,
                             json={"prompt": keywords})
    binary = response.content
    img_buffer = io.BytesIO(binary)
    byte_data = img_buffer.getvalue()
    return base64.b64encode(byte_data)
