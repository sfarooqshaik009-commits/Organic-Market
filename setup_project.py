import os
import sys

# Directory tree configuration
DIRECTORIES = [
    "organic_market_project/organic_market",
    "organic_market_project/store",
    "organic_market_project/static/css",
    "organic_market_project/static/js",
    "organic_market_project/static/images/hero",
    "organic_market_project/static/images/vegetables",
    "organic_market_project/static/images/fruits",
    "organic_market_project/static/images/fertilizers",
    "organic_market_project/templates",
]

# Standard files to generate
FILES = [
    "organic_market_project/manage.py",
    "organic_market_project/organic_market/__init__.py",
    "organic_market_project/organic_market/settings.py",
    "organic_market_project/organic_market/urls.py",
    "organic_market_project/organic_market/wsgi.py",
    "organic_market_project/store/__init__.py",
    "organic_market_project/store/admin.py",
    "organic_market_project/store/apps.py",
    "organic_market_project/store/models.py",
    "organic_market_project/store/serializers.py",
    "organic_market_project/store/views.py",
    "organic_market_project/store/urls.py",
    "organic_market_project/static/css/styles.css",
    "organic_market_project/static/js/app.js",
    "organic_market_project/templates/index.html",
]

def build_structure():
    """Generates folders and placeholder file structures for 60 custom image paths."""
    print("Building Organic Farming Market directory structure...")
    
    for folder in DIRECTORIES:
        os.makedirs(folder, exist_ok=True)
        print(f" Created directory: {folder}")
        
    for filepath in FILES:
        if not os.path.exists(filepath):
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# {os.path.basename(filepath)}\n")
            print(f" Created file: {filepath}")

    # Generate 20 placeholder image references for each category
    categories = {
        "vegetables": "veg_",
        "fruits": "fruit_",
        "fertilizers": "fert_"
    }
    
    for cat, prefix in categories.items():
        dir_path = f"organic_market_project/static/images/{cat}"
        for i in range(1, 21):
            file_name = f"{prefix}{i}.jpg"
            full_path = os.path.join(dir_path, file_name)
            if not os.path.exists(full_path):
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write("") # Placeholder file for customization
    
    print("\nProject structure initialized successfully!")
    print("Place your 20 vegetable, 20 fruit, and 20 fertilizer images into static/images/")

if __name__ == "__main__":
    build_structure()