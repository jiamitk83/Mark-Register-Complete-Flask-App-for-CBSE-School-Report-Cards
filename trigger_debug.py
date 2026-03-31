import requests

# Make a request to trigger the debug print
response = requests.get('http://127.0.0.1:5000/exams')
print('Request made to /exams, check server logs for debug output')