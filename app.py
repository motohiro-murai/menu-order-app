# app.py
import argparse
import os, json
from datetime import datetime, timezone, timedelta
from typing import List, Tuple

from menu_item import Food, Drink, Dessert
from menu_io import load_menus, save_menus

HISTORY_FILE = os.path.join("data", "orders.json")
JST = timezone(timedelta(hours=9))

def build_catalog():
    foods, drinks, desserts = load_menus()
    catalog = []
    for x in foods:
        catalog.append(("Food", x))
    for x in drinks:
        catalog.append(("Drink", x))
    for x in desserts:
        catalog.append(("Dessert", x))
    return catalog

def show_menu(catalog):
    print("メニュー（番号で選択 / m=編集モード / q=終了）")
    print("_" * 50)
    for i, (cat, item) in enumerate(catalog, 1):
        print(f"{i:>2} .[{cat}] {item.info()}")
    print("_" * 50)

def summarize(selected_items):
    total_price   = sum(getattr(it, "price", 0) for it in selected_items)
    total_calorie = sum(getattr(it, "calorie", 0) for it in selected_items)
    total_volume  = sum(getattr(it, "volume_ml", 0) for it in selected_items)
    total_sugar   = sum(getattr(it, "sugar_g", 0) for it in selected_items)
    return total_price, total_calorie, total_volume, total_sugar

def _load_history_safely() -> list:
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        try:
            os.replace(HISTORY_FILE, HISTORY_FILE + ".broken")
        except Exception:
            pass
        return []

def save_order(order: List[Tuple[object, int]]):
    if not order:
        print("（空の注文は保存しませんでした）")
        return

    history = _load_history_safely()
    record = {
        "timestamp": datetime.now(JST).isoformat(timespec="seconds"),
        "items":[{"name":it.name,"qty":qty,"price":getattr(it,"price",0)} for it,qty in order]
    }
    history.append(record)
    with open(HISTORY_FILE,"w",encoding="utf-8") as f:
        json.dump(history,f,ensure_ascii=False,indent=2)
    print(f"📝 注文履歴を保存しました → {HISTORY_FILE}")

def print_receipt(order: List[Tuple[object, int]]):
    if not order:
        print("注文はありませんでした")
        return
    from collections import OrderedDict
    grouped = OrderedDict()
    for item,qty in order:
        grouped.setdefault(item.name, {"item":item,"qty":0})
        grouped[item.name]["qty"] += qty

    print("\n  最終注文内容")
    for name, rec in grouped.items():
        item = rec["item"]; qty = rec["qty"]
        print(f"- {item.info()}  × {qty}")

    total_price   = sum(getattr(r["item"],"price",0)*r["qty"] for r in grouped.values())
    total_calorie = sum(getattr(r["item"],"calorie",0)*r["qty"] for r in grouped.values())
    total_volume  = sum(getattr(r["item"],"volume_ml",0)*r["qty"] for r in grouped.values())
    total_sugar   = sum(getattr(r["item"],"sugar_g",0)*r["qty"] for r in grouped.values())

    print("\n====== 合計 ======")
    print(f"金額: {total_price} 円")
    if total_calorie: print(f"カロリー: {total_calorie} kcal")
    if total_volume:  print(f"ドリンク量: {total_volume} ml")
    if total_sugar:   print(f"糖質: {total_sugar} g")

def show_history():
    history = _load_history_safely()
    if not history:
        print("注文履歴はまだありません")
        return
    latest = history[-1]
    print("\n 最新の注文履歴")
    print(f"日時: {latest.get('timestamp','-')}")
    for item in latest.get("items",[]):
        print(f"{item.get('name','?')} × {item.get('qty','?')} (¥{item.get('price','?')})")
    print("_"*50)

def _print_subtotal(order: List[Tuple[object,int]]):
    if not order: return
    items=[]
    for it,qty in order: items.extend([it]*qty)
    p,k,v,s = summarize(items)
    line = f"— 小計 — 金額: {p} 円"
    if k: line += f" / {k} kcal"
    if v: line += f" / {v} ml"
    if s: line += f" / 糖質 {s} g"
    print(line+"\n")

# ===== ここから編集モード =====
def edit_menu():
    while True:
        print("\n=== メニュー編集モード ===")
        print("[1] 追加  [2] 削除  [b] 戻る")
        sel = input("> ").strip().lower()
        if sel == "b": return
        if sel == "1":
            add_menu_item()
        elif sel == "2":
            delete_menu_item()
        else:
            print("入力が正しくありません。")

def _choose_category() -> str | None:
    print("\nカテゴリを選択してください")
    print("[1] Food  [2] Drink  [3] Dessert  [b] 戻る")
    x = input("> ").strip().lower()
    if x == "1": return "Food"
    if x == "2": return "Drink"
    if x == "3": return "Dessert"
    return None

def add_menu_item():
    cat = _choose_category()
    if not cat: return
    name = input("名前: ").strip()
    if not name:
        print("名前は必須です。"); return
    # 価格
    price_s = input("価格(円): ").strip()
    if not price_s.isdigit() or int(price_s) < 0:
        print("価格は0以上の整数で入力してください。"); return
    price = int(price_s)

    # 追加属性（任意）
    def _opt_int(prompt):
        s = input(prompt).strip()
        if s == "": return None
        if s.isdigit(): return int(s)
        print("整数で入力してください（空Enterでスキップ）。"); return _opt_int(prompt)

    calorie  = _opt_int("カロリー(kcal)［任意］: ")
    volume   = _opt_int("容量(ml)［任意/Drink向け］: ")
    sugar    = _opt_int("糖質(g)［任意］: ")

    foods, drinks, desserts = load_menus()
    if cat == "Food":
        foods.append(Food(name=name, price=price, calorie=calorie or 0))
    elif cat == "Drink":
        drinks.append(Drink(name=name, price=price, volume_ml=volume or 0, sugar_g=sugar or 0))
    else:
        desserts.append(Dessert(name=name, price=price, calorie=calorie or 0, sugar_g=sugar or 0))

    save_menus(foods, drinks, desserts)
    print(f"✅ 追加しました: [{cat}] {name}（¥{price}）")

def delete_menu_item():
    cat = _choose_category()
    if not cat: return
    foods, drinks, desserts = load_menus()
    target = foods if cat=="Food" else drinks if cat=="Drink" else desserts
    if not target:
        print("このカテゴリには項目がありません。"); return

    print("\n削除する項目を選んでください")
    for i, it in enumerate(target, 1):
        print(f"{i:>2}. {it.info()}")
    idx_s = input("> ").strip()
    if not idx_s.isdigit():
        print("番号で入力してください。"); return
    idx = int(idx_s)
    if not (1 <= idx <= len(target)):
        print("範囲外です。"); return
    removed = target.pop(idx-1)
    save_menus(foods, drinks, desserts)
    print(f"🗑️ 削除しました: {removed.name}")

# ===== メイン =====
def main():
    parser = argparse.ArgumentParser(description="メニュー注文アプリ")
    parser.parse_args()

    order: List[Tuple[object,int]] = []

    while True:
        catalog = build_catalog()
        if not catalog:
            print("メニューが空です。data/menus.json を確認してください。")
            return

        show_menu(catalog)
        choice = input("注文番号 / m=編集 / q=終了: ").strip().lower()

        if choice == "q":
            break
        if choice == "m":
            edit_menu()
            continue
        if not choice.isdigit():
            print("⚠️ 入力が正しくありません。\n"); continue

        idx = int(choice)
        if not (1 <= idx <= len(catalog)):
            print("⚠️ 番号が範囲外です。\n"); continue

        item = catalog[idx-1][1]
        qty_s = input(f"{item.name} の数量（Enter=1 / c=取消 / q=終了）: ").strip().lower()
        if qty_s == "q": break
        if qty_s == "c": print("取消しました。\n"); continue
        qty = 1 if qty_s == "" else int(qty_s) if qty_s.isdigit() and int(qty_s)>0 else None
        if qty is None:
            print("⚠️ 数量は正の整数で入力してください。\n"); continue

        order.append((item, qty))
        print(f"{item.name} を {qty} 個追加しました。\n")
        _print_subtotal(order)

    print_receipt(order)
    save_order(order)
    show_history()

if __name__ == "__main__":
    main()