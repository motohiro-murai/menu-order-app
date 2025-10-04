def summarize(selected_items):
    total_price   = sum(it.price for it in selected_items)
    total_calorie = sum(getattr(it, "calorie", 0) for it in selected_items)
    total_volume  = sum(getattr(it, "volume_ml", 0) for it in selected_items)
    total_sugar   = sum(getattr(it, "sugar_g", 0) for it in selected_items)
    return total_price, total_calorie, total_volume, total_sugar


def print_receipt(order):
    """(item, qty) のリスト order を集計してレシート出力"""
    if not order:
        
        print("注文はありませんでした。")
        return

    from collections import OrderedDict
    grouped = OrderedDict()
    for item, qty in order:
        if item.name in grouped:
            grouped[item.name]["qty"] += qty
        else:
            grouped[item.name] = {"item": item, "qty": qty}

    print("\n🧾 最終注文内容")
    for name, rec in grouped.items():
        item = rec["item"]
        qty  = rec["qty"]
        print(f"- {item.info()} ×{qty}")

    total_price   = sum(rec["item"].price                  * rec["qty"] for rec in grouped.values())
    total_calorie = sum(getattr(rec["item"], "calorie", 0) * rec["qty"] for rec in grouped.values())
    total_volume  = sum(getattr(rec["item"], "volume_ml",0)* rec["qty"] for rec in grouped.values())
    total_sugar   = sum(getattr(rec["item"], "sugar_g", 0) * rec["qty"] for rec in grouped.values())

    print("\n====== 合計 ======")
    print(f"💰 金額: {total_price} 円")
    if total_calorie:
        print(f"🔥 カロリー: {total_calorie} kcal")
    if total_volume:
        print(f"🥤 ドリンク量: {total_volume} ml")
    if total_sugar:
        print(f"🍰 糖質: {total_sugar} g")