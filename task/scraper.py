import requests
from bs4 import BeautifulSoup
from http import HTTPStatus

url = input('Input the URL:')
r = requests.get(url)

if r.status_code == HTTPStatus.OK:

    with open('source.html', 'wb') as file:
        file.write(bytes(r.content))
        print("Content saved.")
else:
    print('The URL returned ', r.status_code)
