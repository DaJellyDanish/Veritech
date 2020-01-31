import requests
import re
import nltk
import heapq
from bs4 import BeautifulSoup
from requests import get


subscription_key = "7089442e36fa485c88adf510b87dc1aa"
search_url = "https://news-search-veritech.cognitiveservices.azure.com/bing/v7.0/news/search"
headers = {"Ocp-Apim-Subscription-Key" : subscription_key}


def get_articles(searchterm):
    search_term = searchterm
    params = {"q": search_term, "textDecorations": False, "textFormat": "HTML", "count": 5, "freshness": "Week"}
    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()
    search_results = response.json()
    return search_results["value"]

def summarize(text):
        text = re.sub(r'\[[0-9]*\]', ' ', text)
        text = re.sub(r'\s+', ' ', text)

        formatted_text = re.sub('[^a-zA-Z]', ' ', text)
        formatted_text = re.sub(r'\s+', ' ', formatted_text)

        sentence_list = nltk.sent_tokenize(text)

        stopwords = nltk.corpus.stopwords.words('english')

        word_frequencies = {}
        for word in nltk.word_tokenize(formatted_text):
            if word not in stopwords:
                if word not in word_frequencies.keys():
                    word_frequencies[word] = 1
                else:
                    word_frequencies[word] += 1

        sentence_scores = {}
        for sent in sentence_list:
            for word in nltk.word_tokenize(sent.lower()):
                if word in word_frequencies.keys():
                    if len(sent.split(' ')) < 30:
                        if sent not in sentence_scores.keys():
                            sentence_scores[sent] = word_frequencies[word]
                        else:
                            sentence_scores[sent] += word_frequencies[word]

        summary_sentences = heapq.nlargest(5, sentence_scores, key=sentence_scores.get)
        summary = ' '.join(summary_sentences)
        return summary

def scrape(article_list):
    counter = 0
    summary_list = []
    for x in article_list:
        text = ""
        response = get(x["url"])
        soup = BeautifulSoup(response.text, 'html.parser')
        page = soup.find_all('p')
        for x in page:
            text += x.getText() + "\n"
        out = summarize(text)
        summary_list.append(out)
    return summary_list
