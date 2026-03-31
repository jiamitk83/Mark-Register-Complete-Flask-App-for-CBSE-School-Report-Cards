try:
    from app import app
    print("App imported successfully")
    print("Routes:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.rule} -> {rule.endpoint}")
except Exception as e:
    print(f"Error importing app: {e}")
    import traceback
    traceback.print_exc()