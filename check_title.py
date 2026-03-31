import requests

response = requests.get('http://127.0.0.1:5000/exams')
if 'DEBUG:' in response.text:
    # Find the title line
    lines = response.text.split('\n')
    for line in lines:
        if 'DEBUG:' in line:
            print('Title with debug:', line.strip())
else:
    print('No DEBUG found in title')