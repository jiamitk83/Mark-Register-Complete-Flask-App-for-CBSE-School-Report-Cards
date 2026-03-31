import requests

response = requests.get('http://127.0.0.1:5000/exams')
if 'DEBUG:' in response.text:
    print('Found debug output in response')
    # Extract the debug line
    lines = response.text.split('\n')
    for line in lines:
        if 'DEBUG:' in line:
            print('Debug line:', line.strip())
else:
    print('No debug output found')
    print('Contains No Custom Exams:', 'No Custom Exams Created' in response.text)