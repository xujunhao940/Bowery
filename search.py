import random
import requests
from bs4 import BeautifulSoup
import datetime

searchSchema = {'function_declarations': [
    {'name': 'search',
     'description': """Search the internet.""",
     'parameters': {'type_': 'OBJECT',
                    'properties': {
                        'keywords': {'type_': 'STRING',
                                     'description': "Keyword to search."},
                        'question': {'type_': 'STRING',
                                     'description': """The follow-up question after searching.
                                 If there are no follow-up questions, the question should be 'summary'
                                 e.g. 
                                 1. prompt:Search for Taylor Swift's latest album
                                 keywords:Taylor Swift latest album
                                 question:What is Taylor Swift's latest album
                                 2. prompt:Search for Taylor Swift
                                 keywords:Taylor Swift
                                 question:summary
                                 """}
                    },
                    'required': ['keywords', 'question']}}]}


def search(keyword, question):
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
        'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1 Safari/605.1.15'
    ]

    keyword = keyword
    response = requests.get(f"https://www.google.com/search?q={keyword}",
                            headers={'User-Agent': random.choice(USER_AGENTS)})
    soup = BeautifulSoup(response.content, 'html.parser')
    search_results = soup.select('div.g')
    urls = []
    for result in search_results:
        link = result.select_one('a')
        if link.has_attr('href'):
            title = link.get_text(strip=True)
            date_tag = result.select_one('span.f')
            if date_tag:
                date = date_tag.text
            else:
                date_tag = result.select_one('span.st')
                if date_tag:
                    text = date_tag.get_text()
                    match = re.search(r'(\d{4}年\d{1,2}月\d{1,2}日|\d{4}-\d{2}-\d{2})', text)
                    if match:
                        date = match.group(0)
                    else:
                        date = "Unknown date"
                else:
                    date = "Unknown date"
            urls.append([link['href'], title, date])
    webs = []
    for content in urls[:5]:
        try:
            response = requests.get(content[0], headers={'User-Agent': random.choice(USER_AGENTS)})
            soup = BeautifulSoup(response.content, 'html.parser')
            text_elements = []
            for tag in ['p', 'div', 'span']:
                text_elements.extend(soup.find_all(tag))
            text = '\n'.join([element.get_text(strip=True) for element in text_elements])
            webs.append(content + [text])
        except:
            continue
    formatted_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prompt = f"""
    You are a knowledgeable and helpful person who can answer any question. Your task is to answer the question below.

    Question: {question}

    The question itself, or part of it, may require information from the internet to give a satisfactory answer. The related search results below, separated by three backticks, have provided the necessary information to set the context for the question, so you do not need to access the internet to answer the question.

    For your reference, today's date is {formatted_datetime}.

    ---

    If you use any search results in your answer, always cite the source at the end of the corresponding line, similar to Wikipedia.org citations. Use the format [[NUMBER](URL)], where NUMBER and URL correspond to the provided search results below, separated by three backticks.

    Present the answer in a clear format.
    If necessary, use numbered lists to clarify things.
    Try to keep the answer concise, ideally no more than 1000 words.

    ---

    If there is not enough information in the search results, do your best to give a helpful response using all the information from the search results.

    """
    for i in range(len(webs)):
        web = webs[i]
        prompt += f"""
        NUMBER: {i}
        URL: {web[0]}
        TITLE: {web[1]}
        DATE: {web[2]}
        CONTENT:
        {web[3]}
        """

    return prompt
