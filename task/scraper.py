import requests

url = input('Input the URL:')

r = requests.get(url)
print(r.content)

if r.status_code == 200 and 'content' is r.json():
    print(r.json()['content'])
else:
    print('Invalid quote resource!')