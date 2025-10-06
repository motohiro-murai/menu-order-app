# menu_io.py
import os, json
from menu_item import Food, Drink, Dessert

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "menus.json")

def _pick(d: dict, keys: list[str]) -> dict:
    """辞書 d から指定キーのみ拾って返す（存在するものだけ）"""
    return {k: d[k] for k in keys if k in d}

def load_menus():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        # 初期ファイルが無ければ空を作る
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({"foods": [], "drinks": [], "desserts": []}, f, ensure_ascii=False, indent=2)
        return [], [], []

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        raw = json.load(f)

    # --- foods ---
    foods = [Food(**_pick(d, ["name", "price", "calorie"])) for d in raw.get("foods", [])]

    # --- drinks ---
    drinks = []
    for d in raw.get("drinks", []):
        dd = dict(d)
        # 足りない場合のフォールバック（任意）
        if "sugar_g" not in dd and "sugar" in dd:
            dd["sugar_g"] = dd["sugar"]
        drinks.append(Drink(**_pick(dd, ["name", "price", "volume_ml", "sugar_g"])))

    # --- desserts ---
    desserts = []
    for d in raw.get("desserts", []):
        dd = dict(d)
        # sugar_g が無い場合、calorie を代用（あなたの意図に合わせた仕様）
        if "sugar_g" not in dd and "calorie" in dd:
            dd["sugar_g"] = dd["calorie"]
        desserts.append(Dessert(**_pick(dd, ["name", "price", "sugar_g"])))

    return foods, drinks, desserts

def save_menus(foods, drinks, desserts):
    """現在のメニューを menus.json に保存"""
    os.makedirs(DATA_DIR, exist_ok=True)
    data = {
        "foods": [
            {"name": f.name, "price": f.price, "calorie": getattr(f, "calorie", 0)}
            for f in foods
        ],
        "drinks": [
            {"name": d.name, "price": d.price, "volume_ml": getattr(d, "volume_ml", 0), "sugar_g": getattr(d, "sugar_g", 0)}
            for d in drinks
        ],
        "desserts": [
            {"name": s.name, "price": s.price, "sugar_g": getattr(s, "sugar_g", 0)}
            for s in desserts
        ],
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)