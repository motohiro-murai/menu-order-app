from menu_io import load_menus

DISCOUNT_THRESHOLD = 1500   # 割引が効く合計額
DISCOUNT_RATE = 0.1         # 10%OFF

def choose(items, label):
    print(f"\n=== {label} メニュー ===")
    for i, it in enumerate(items):
        print(f"{i}: {it.info()}")
    s = input(f"{label}番号（Enterでスキップ）: ").strip()
    if not s:
        return None, 0
    if not s.isdigit() or not (0 <= int(s) < len(items)):
        print("⚠ 無効な番号です。スキップします。")
        return None, 0
    qty_s = input("個数: ").strip()
    qty = int(qty_s) if qty_s.isdigit() else 1
    qty = max(1, min(qty, 100))
    return items[int(s)], qty

def main():
    foods, drinks, desserts = load_menus()
    order = []

    for items, label in [(foods, "Food"), (drinks, "Drink"), (desserts, "Dessert")]:
        it, qty = choose(items, label)
        if it and qty:
            order.append((it, qty))

    if not order:
        print("\n（何も選ばれていません）")
        return

    subtotal = sum(it.price * qty for it, qty in order)
    calories = sum(getattr(it, "calorie", 0) * qty for it, qty in order)
    discount = int(subtotal * DISCOUNT_RATE) if subtotal >= DISCOUNT_THRESHOLD else 0
    total = subtotal - discount

    print("\n=== 注文確認 ===")
    for it, qty in order:
        print(f"{it.name} x {qty} = ¥{it.price * qty}")
    print(f"小計: ¥{subtotal}")
    if discount:
        print(f"割引: -¥{discount}（{int(DISCOUNT_RATE*100)}%オフ）")
    print(f"合計: ¥{total}")
    if calories:
        print(f"推定カロリー: {calories} kcal")

if __name__ == "__main__":
    main()
    