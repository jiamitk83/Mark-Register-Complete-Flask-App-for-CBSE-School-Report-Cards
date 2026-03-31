from flask import Flask

app = Flask(__name__)

print("Before route definition")
print("Routes before:", len(list(app.url_map.iter_rules())))

@app.route('/test')
def test():
    return 'test'

print("After route definition")
print("Routes after:", len(list(app.url_map.iter_rules())))

for rule in app.url_map.iter_rules():
    print(f"  {rule.rule} -> {rule.endpoint}")