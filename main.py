import json
from flask import Flask, render_template, request, stream_with_context
from PIL import Image
import base64
import io
import google.generativeai as genai
from config import api_token
import wikipedia
import requests

if api_token == "YOUR_API_TOKEN":
    raise Exception("Replace `YOUR_API_TOKEN` with your Gemini API token in `config.py`")

searchSchema = {'function_declarations': [
    {'name': 'search',
     'description': """Search the Google/Wikipedia.""",
     'parameters': {'type_': 'OBJECT',
                    'properties': {
                        'website': {"type": "string",
                                    'description': "Google or Wikipedia.If the user does not specify, use Wikipedia as the website"},
                        'lang': {'type': 'string', 'description': "The language the user speaks"},
                        'query': {'type': 'string',
                                  'description': "Google: Questions asked by users; Wikipedia: Objects asked by users"},
                        'then': {'type': 'string',
                                 'description': """Available when website is Wikipedia. It's question after finding 'query' on wikipedia. If there are no questions, it should be 'summary'. e.g. question:how much albums does Taylor Swift have query:taylor swift albums then:how much albums does she have; question:how old is Taylor Swift have query:taylor swift then:how old is she"""}
                    },
                    'required': ['query', 'website', 'then', 'lang']}}]}


def search(query, website, then, lang):
    website = "Wikipedia"
    if website == "Google":
        return f"Searching Google for {query}"
    else:
        language_code = 'en'
        headers = {'User-Agent': 'Bowery (https://github.com/xujunhao940/bowery/)'}
        base_url = 'https://api.wikimedia.org/core/v1/wikipedia/'
        endpoint = '/search/page'
        url = base_url + language_code + endpoint
        parameters = {'q': query, 'limit': 2}
        response = requests.get(url, headers=headers, params=parameters)
        if response.json()["pages"][0]["description"] == "Topics referred to by the same term":
            page = response.json()["pages"][1]
        else:
            page = response.json()["pages"][0]
    page = wikipedia.page(pageid=page["id"])
    if then == "summary":
        return {
            "type": "search",
            "website": "Wikipedia",
            "mode": "summary",
            "q": query,
            "title": page.title,
            "url": page.url,
            "summary": page.summary,
            "lang": lang,
            "pageid": page.pageid
        }
    return {
        "type": "search",
        "website": "Wikipedia",
        "mode": "then",
        "q": query,
        "title": page.title,
        "url": page.url,
        "summary": page.summary,
        "pageid": page.pageid,
        "lang": lang,
        "then": then
    }


app = Flask(__name__)
genai.configure(api_key=api_token)

generation_config = genai.GenerationConfig(
    temperature=0.2,
    response_mime_type="text/plain",
)

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-latest",
    generation_config=generation_config,
    system_instruction="You are an assistant called Bowery. You don’t have to ask when the user doesn’t ask to search. Search only when the user explicitly states that they want to search. When searching, all are based on the search content. Answer in the language the user speaks.",
    tools=[searchSchema]
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

        func_conf = None

        for chunk in response:
            print(chunk.candidates)
            if "text" in chunk.candidates[0].content.parts[0]:
                yield json.dumps({"type": "answer", "text": chunk.text})
                yield "-|BOWERY SPLIT|-"

        response.resolve()

        if "text" not in response.candidates[0].content.parts[0]:
            func_conf = response.candidates[0].content.parts[0].function_call

        if func_conf:
            result = search(func_conf.args["query"], func_conf.args["website"], func_conf.args["then"], func_conf.args["lang"])
            yield json.dumps(result)

    return stream_with_context(stream())


@app.route('/answer', methods=['GET', 'POST'])
def answer():
    def stream():
        data = json.loads(request.data)
        page = wikipedia.page(pageid=data["pageid"])
        response = model.generate_content(f"""
                Please answer the questions based on the given text. Then translate the answer into the given language.
                Output only translation results.No translation is required for specific names etc.
                language: {data['lang']}
                text: {page.summary}
                question: {data['then']}
                translated answer:
                """, stream=True)
        for chunk in response:
            yield chunk.text

    return stream_with_context(stream())


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8888, debug=True, ssl_context=('cert/server.crt', 'cert/server.key'))
