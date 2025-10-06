# menu_io.py
import os, json
from menu_item import Food, Drink, Dessert

DATA_DIR  = "data"
DATA_FILE = os.path.join(DATA_DIR, "menus.json")

def load_menus():
    os.makedirs(DATA_DIR, exist_ok=True)

    # 初回は空テンプレを作成
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({"foods": [], "drinks": [], "desserts": []}, f, ensure_ascii=False, indent=2)
        return [], [], []

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        raw = json.load(f)

    # ---- 取り込み（フォーマットを厳密化 & 後方互換）----
    foods = [Food(**_pick(d, ["name", "price", "calorie"])) for d in raw.get("foods", [])]

    # ドリンクは金額＋容量のみ（sugar_g は渡さない）
    drinks = [Drink(**_pick(d, ["name", "price", "volume_ml"])) for d in raw.get("drinks", [])]

    # デザートは糖質のみ。もし誤って "calorie" が入っていたら sugar_g に読み替える
    desserts_raw = raw.get("desserts", [])
    desserts = []
    for d in desserts_raw:
        dd = dict(d)
        if "sugar_g" not in dd and "calorie" in dd:
            # 互換：以前の誤保存(カロリー)を糖質扱いに補正
            dd["sugar_g"] = dd.get("calorie", 0)
        desserts.append(Dessert(**_pick(dd, ["name", "price", "sugar_g"])))

    return foods, drinks, desserts


def save_menus(foods, drinks, desserts):
    """現在のメニューを menus.json に保存"""
    os.makedirs(DATA_DIR, exist_ok=True)
    data = {
        "foods":    [{"name": f.name, "price": f.price, "calorie": getattr(f, "calorie", 0)} for f in foods],
        "drinks":   [{"name": d.name, "price": d.price, "volume_ml": getattr(d, "volume_ml", 0)} for d in drinks],
        # デザートは sugar_g だけ（calorie は書かない）
        "desserts": [{"name": s.name, "price": s.price, "sugar_g": getattr(s, "sugar_g", 0)} for s in desserts],
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _pick(d: dict, keys: list[str]) -> dict:
    """辞書 d から指定キーのみ拾って返す（存在するものだけ）"""
    return {k: d.get(k) for k in keys if k in d}