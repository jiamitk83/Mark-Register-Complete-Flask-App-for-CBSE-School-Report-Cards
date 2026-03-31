from app import app, get_db
import json

with app.app_context():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM custom_exams ORDER BY created_at DESC')
    exams = [dict(row) for row in cursor.fetchall()]
    conn.close()

    print(f"Found {len(exams)} exams in database:")
    for exam in exams:
        print(f"  - {exam['exam_name']}")

    # Process exams like the route does
    for exam in exams:
        exam['classes'] = json.loads(exam['classes'])
        exam['sections'] = json.loads(exam['sections'])
        exam['subjects'] = json.loads(exam['subjects'])
        if exam.get('students'):
            exam['students'] = json.loads(exam['students'])

    print(f"After processing, {len(exams)} exams ready for template")

    # Test template rendering
    from flask import render_template_string
    template_content = """
    {% if exams %}
        <div class="row">
            {% for exam in exams %}
                <div class="card">
                    <h5>{{ exam.exam_name }}</h5>
                    <div class="button-group">
                        <a href="#" class="btn btn-warning">Edit</a>
                        <form method="POST">
                            <button type="submit" class="btn btn-danger">Delete</button>
                        </form>
                    </div>
                </div>
            {% endfor %}
        </div>
    {% else %}
        <p>No exams found</p>
    {% endif %}
    """

    rendered = render_template_string(template_content, exams=exams)
    print("Template rendered successfully!")
    print("Contains 'Edit':", 'Edit' in rendered)
    print("Contains 'Delete':", 'Delete' in rendered)