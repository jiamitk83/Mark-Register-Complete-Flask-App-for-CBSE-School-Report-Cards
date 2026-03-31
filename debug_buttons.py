import requests

try:
    response = requests.get('http://127.0.0.1:5000/exams')
    html = response.text

    print("=== BUTTON VISIBILITY DEBUG ===")

    # Check for button text
    if 'Edit' in html and 'Delete' in html:
        print('✅ Edit and Delete TEXT found in HTML')
        edit_count = html.count('Edit')
        delete_count = html.count('Delete')
        print(f'Edit occurrences: {edit_count}, Delete occurrences: {delete_count}')
    else:
        print('❌ Edit and Delete TEXT NOT found in HTML')

    # Check for button classes
    if 'btn-warning' in html:
        print('✅ btn-warning class found (Edit button)')
    else:
        print('❌ btn-warning class NOT found')

    if 'btn-danger' in html:
        print('✅ btn-danger class found (Delete button)')
    else:
        print('❌ btn-danger class NOT found')

    # Check for button-group class
    if 'button-group' in html:
        print('✅ button-group class found')
    else:
        print('❌ button-group class NOT found')

    # Check for form elements
    if '<form' in html and 'method="POST"' in html:
        print('✅ Delete form found')
    else:
        print('❌ Delete form NOT found')

    # Check for CSS styles
    if '!important' in html:
        print('✅ CSS !important overrides found')
    else:
        print('❌ CSS !important overrides NOT found')

    print("\n=== EXTRACTING BUTTON HTML ===")
    # Extract button section
    start = html.find('button-group')
    if start != -1:
        end = html.find('</div>', start)
        if end != -1:
            button_html = html[start:end+6]
            print("Button HTML found:")
            print(button_html[:500] + "..." if len(button_html) > 500 else button_html)
        else:
            print("❌ Could not find end of button section")
    else:
        print("❌ button-group class not found in HTML")

except Exception as e:
    print(f'❌ Error: {e}')