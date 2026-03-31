import requests

try:
    # Test debug endpoint
    response = requests.get('http://127.0.0.1:5000/debug-exams')
    print('DEBUG ENDPOINT:', response.text)

    # Test main exams endpoint
    response2 = requests.get('http://127.0.0.1:5000/exams')
    if 'No Custom Exams Created' in response2.text:
        print('❌ MAIN ENDPOINT: Showing "No Custom Exams Created"')
    elif 'Edit' in response2.text:
        print('✅ MAIN ENDPOINT: Edit buttons found')
    else:
        print('❓ MAIN ENDPOINT: Exams section found but no Edit buttons')

except Exception as e:
    print(f'Error: {e}')