import requests

r = requests.get('http://127.0.0.1:5000/exams')
print('DEBUG in title:', 'DEBUG' in r.text)