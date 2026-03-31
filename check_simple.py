import requests

r = requests.get('http://127.0.0.1:5000/exams')
print('Response contains Found:', 'Found' in r.text)
print('First 200 chars:', r.text[:200])