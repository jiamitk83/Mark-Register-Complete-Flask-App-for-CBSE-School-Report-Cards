import requests

response = requests.get('http://127.0.0.1:5000/exams')
print('Contains btn-warning:', 'btn-warning' in response.text)
print('Contains btn-danger:', 'btn-danger' in response.text)
print('Contains button-group:', 'button-group' in response.text)
print('Contains Edit:', 'Edit' in response.text)
print('Contains Delete:', 'Delete' in response.text)