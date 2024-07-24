import requests
from bs4 import BeautifulSoup

url = input('Input the URL:')
r = requests.get(url)

if r.status_code == 200 and url.startswith('https://www.nature.com/articles/'):

    soup = BeautifulSoup(r.content, 'html.parser')
    title = soup.title.string
    description = soup.find('meta', {'name' : 'description'})['content']

    article_info = {
        "title": title,
        "description": description
    }

    print(article_info)
else:
    print('Invalid page!')
