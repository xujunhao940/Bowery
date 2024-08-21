import json
from flask import Flask, render_template, request, stream_with_context
from PIL import Image
import base64
import io
import google.generativeai as genai
from config import gemini_api_token, tools_config

if gemini_api_token == "YOUR_API_TOKEN":
    raise Exception("Replace `YOUR_API_TOKEN` with your Gemini API token in `config.py`")

tools = []
if tools_config["search"]:
    from search import search, searchSchema
    tools.append(searchSchema)
if tools_config["paint"]:
    from paint import paint, paintSchema
    tools.append(paintSchema)

app = Flask(__name__)
genai.configure(api_key=gemini_api_token)

generation_config = genai.GenerationConfig(
    temperature=0.2
)

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-latest",
    generation_config=generation_config,
    system_instruction="You are an assistant called Bowery. "
                       "You don’t have to ask when the user doesn’t ask to call the function."
                       "Call the function only when the user explicitly states that they want to call the function."
                       "Answer in the language the user speaks.",
    tools=tools
)

apiModel = genai.GenerativeModel(
    model_name="gemini-1.5-flash-latest",
    generation_config=generation_config,
    system_instruction="You are an assistant called Bowery. "
                       "Answer in the language the user speaks."
)

chat_session = model.start_chat()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    def stream():
        data = json.loads(request.data)
        if data["image"] == "Undefined":
            response = chat_session.send_message(data["message"], stream=True)
        else:
            img_data = base64.b64decode(data["image"])
            image = Image.open(io.BytesIO(img_data))
            response = chat_session.send_message([data["message"], image], stream=True)

        for chunk in response:
            for part in chunk.parts:
                if len(part.text) != 0:
                    print(part.text)
                    yield json.dumps({"type": "text", "message": part.text})
                    yield "-|BOWERY SPLIT|-"

        for part in response.parts:
            if len(part.text) == 0:
                if part.function_call.name == "search":
                    print("search")
                    prompt = search(part.function_call.args["keywords"], part.function_call.args["question"])

                    response = model.generate_content(prompt, stream=True)
                    for chunk in response:
                        yield json.dumps({"type": "text", "message": chunk.text})
                        yield "-|BOWERY SPLIT|-"
                if part.function_call.name == "paint":
                    print("paint")
                    response = paint(part.function_call.args["keywords"])
                    yield json.dumps({"type": "image", "message": response.decode()})
                    yield "-|BOWERY SPLIT|-"

    return stream_with_context(stream())


@app.route('/api', methods=['GET', 'POST'])
def api():
    data = json.loads(request.data)
    if data["image"] == "Undefined":
        response = apiModel.generate_content(data["text"])
    else:
        img_data = base64.b64decode(data["image"])
        image = Image.open(io.BytesIO(img_data))
        response = apiModel.generate_content([data["text"], image])
    return response.text.encode("gb18030")


if __name__ == '__main__':
    # app.run(host="0.0.0.0", port=8888, debug=True, ssl_context=('cert/server.crt', 'cert/server.key'))
    app.run(host="0.0.0.0", port=8888, debug=True)