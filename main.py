import json
from flask import Flask, render_template, request, stream_with_context
from PIL import Image
import base64
import io
import google.generativeai as genai
from config import api_token

if api_token == "YOUR_API_TOKEN":
    raise Exception("Replace `YOUR_API_TOKEN` with your Gemini API token in `config.py`")

app = Flask(__name__)
genai.configure(api_key=api_token)

generation_config = genai.GenerationConfig(
    temperature=0.9,
    response_mime_type="text/plain",
)

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config
)

chat_session = model.start_chat(
    history=[]
)


@app.route('/')
def index():
    return render_template('main.html')


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    def stream():
        data = json.loads(request.data)
        if data["photo"] == "":
            response = chat_session.send_message(data["message"], stream=True)
        else:
            img_data = base64.b64decode(data["photo"])
            image = Image.open(io.BytesIO(img_data))
            response = chat_session.send_message([data["message"], image], stream=True)
        for chunk in response:
            yield chunk.text

    return stream_with_context(stream())


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8888, debug=True, ssl_context=('cert/server.crt', 'cert/server.key'))
