import requests

try:
    response = requests.get('http://127.0.0.1:5000/exams')
    print('Status:', response.status_code)
    print('Length:', len(response.text))
    print('Contains Edit:', 'Edit' in response.text)
    print('Contains exams:', 'exams' in response.text)
    print('Contains No Custom Exams:', 'No Custom Exams Created' in response.text)
    print('First 500 chars:')
    print(response.text[:500])
except Exception as e:
    print(f'Error: {e}')