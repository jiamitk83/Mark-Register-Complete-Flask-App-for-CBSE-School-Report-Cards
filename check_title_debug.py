import requests

response = requests.get('http://127.0.0.1:5000/exams')
print('Contains DEBUG:', 'DEBUG:' in response.text)
if 'DEBUG:' in response.text:
    start = response.text.find('DEBUG:')
    end = response.text.find(')', start)
    if end > start:
        debug_part = response.text[start:end+1]
        print('Debug part:', debug_part)