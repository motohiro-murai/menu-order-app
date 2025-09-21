import json, os
from menu_item import Food, Drink, Dessert

DATA_DIR = "data"
MENU_FILE = os.path.join(DATA_DIR, "menus.json")

def ensure_data():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(MENU_FILE):
        sample = {
            "foods": [
                {"name": "カレー", "price": 700, "calorie": 850},
                {"name": "からあげ定食", "price": 900, "calorie": 980}
            ],
            "drinks": [
                {"name": "コーラ", "price": 200, "volume_ml": 350},
                {"name": "アイスコーヒー", "price": 250, "volume_ml": 300}
            ],
            "desserts": [
                {"name": "プリン", "price": 300, "sugar_g": 22},
                {"name": "チーズケーキ", "price": 420, "sugar_g": 18}
            ]
        }
        with open(MENU_FILE, "w", encoding="utf-8") as f:
            json.dump(sample, f, ensure_ascii=False, indent=2)

def load_menus():
    ensure_data()
    with open(MENU_FILE, "r", encoding="utf-8") as f:
        d = json.load(f)
    foods = [Food.from_dict(x) for x in d.get("foods", [])]
    drinks = [Drink.from_dict(x) for x in d.get("drinks", [])]
    desserts = [Dessert.from_dict(x) for x in d.get("desserts", [])]
    return foods, drinks, desserts