import string

import requests
from bs4 import BeautifulSoup
from http import HTTPStatus


def modify_title(title_string):
    modified_title = title_string.strip()
    # for c in title_string.strip():
    #     if c not in string.punctuation:
    #         print(c)
    #         modified_title += c

    modified_title = modified_title.translate(str.maketrans('', '', string.punctuation))
    modified_title = modified_title.replace(" ", "_")

    modified_title += ".txt"

    return modified_title


url = "https://www.nature.com/nature/articles?sort=PubDate&year=2020&page=3"
r = requests.get(url)
saved_artciles = []

if r.status_code == HTTPStatus.OK:
    soup = BeautifulSoup(r.content, 'html.parser')

    articles = soup.find_all('article')

    for i in range(len(articles)):
        article_type = articles[i].find('span', {"data-test": "article.type"}).text

        if article_type.strip().lower() == "news":
            article_link = articles[i].find('a', {"data-track-action": "view article"})['href']

            # print("https://www.nature.com" + article_link)
            article_req = requests.get("https://www.nature.com" + article_link)

            if article_req.status_code == HTTPStatus.OK:
                article_soup = BeautifulSoup(article_req.content, 'html.parser')

                filename = modify_title(article_soup.title.string)
                article_body = article_soup.find("p", {"class": "article__teaser"})
                if article_body:
                    with open(filename, "w") as file:
                        file.write(article_body.text)
                        saved_artciles.append(filename)

    print("Saved articles: ", saved_artciles)
else:
    print('The URL returned ', r.status_code)
