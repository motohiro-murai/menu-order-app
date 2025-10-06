from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime
import os, json
from menu_io import load_menus  # 既存関数を利用

app = Flask(__name__)
app.secret_key = "change-this-in-prod"  # セッションキー（とりあえず固定）

DATA_DIR = "data"
ORDERS_FILE = os.path.join(DATA_DIR, "orders.json")

def ensure_files():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)

def get_catalog():
    foods, drinks, desserts = load_menus()
    catalog = []
    idx = 1
    for x in foods:
        catalog.append({"id": f"F{idx}", "cat": "Food", "name": x.name, "price": x.price, "extra": getattr(x, "calorie", None)}); idx += 1
    idx = 1
    for x in drinks:
        catalog.append({"id": f"D{idx}", "cat": "Drink", "name": x.name, "price": x.price, "extra": getattr(x, "volume_ml", None)}); idx += 1
    idx = 1
    for x in desserts:
        catalog.append({"id": f"S{idx}", "cat": "Dessert", "name": x.name, "price": x.price, "extra": getattr(x, "calorie", None)}); idx += 1
    return catalog

def cart_init():
    if "cart" not in session:
        session["cart"] = []
        session.modified = True

@app.route("/", methods=["GET"])
def show_menu():
    ensure_files(); cart_init()
    catalog = get_catalog()
    return render_template("menu.html", catalog=catalog)

@app.route("/add", methods=["POST"])
def add_to_cart():
    cart_init()
    item_id = request.form.get("id")
    name = request.form.get("name")
    price = int(request.form.get("price", "0"))
    qty = int(request.form.get("qty", "1"))
    cat = request.form.get("cat")
    if qty <= 0:
        flash("数量は1以上を指定してください。"); return redirect(url_for("show_menu"))
    for it in session["cart"]:
        if it["id"] == item_id:
            it["qty"] += qty; break
    else:
        session["cart"].append({"id": item_id, "name": name, "price": price, "qty": qty, "cat": cat})
    session.modified = True
    flash(f"{name} をカートに追加しました。")
    return redirect(url_for("show_menu"))

@app.route("/cart", methods=["GET", "POST"])
def view_cart():
    cart_init()
    if request.method == "POST":
        action = request.form.get("action")
        item_id = request.form.get("id")
        if action == "update":
            qty = int(request.form.get("qty", "1"))
            for it in session["cart"]:
                if it["id"] == item_id:
                    it["qty"] = max(1, qty); break
        elif action == "remove":
            session["cart"] = [it for it in session["cart"] if it["id"] != item_id]
        session.modified = True
        return redirect(url_for("view_cart"))
    total = sum(it["price"] * it["qty"] for it in session["cart"])
    return render_template("cart.html", cart=session["cart"], total=total)

@app.route("/checkout", methods=["POST"])
def checkout():
    cart_init()
    if not session["cart"]:
        flash("カートが空です。"); return redirect(url_for("show_menu"))
    order = {
        "id": datetime.now().strftime("%Y%m%d-%H%M%S"),
        "items": session["cart"],
        "total": sum(it["price"] * it["qty"] for it in session["cart"]),
        "ts": datetime.now().isoformat(timespec="seconds")
    }
    with open(ORDERS_FILE, "r", encoding="utf-8") as f:
        arr = json.load(f)
    arr.append(order)
    with open(ORDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(arr, f, ensure_ascii=False, indent=2)
    session["cart"] = []; session.modified = True
    return render_template("order_complete.html", order=order)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    ensure_files()
    menus_path = os.path.join(DATA_DIR, "menus.json")

    # メニューを読み込む
    with open(menus_path, "r", encoding="utf-8") as f:
        menus = json.load(f)

    if request.method == "POST":
        category = request.form.get("category")
        name = request.form.get("name")
        price = int(request.form.get("price", 0))
        extra = int(request.form.get("extra", 0))

        if not name or price <= 0:
            flash("商品名と価格は必須です。")
            return redirect(url_for("admin"))

        # カテゴリに応じてキーを決める
        if category == "Food":
            menus["foods"].append({"name": name, "price": price, "calorie": extra})
        elif category == "Drink":
            menus["drinks"].append({"name": name, "price": price, "volume_ml": extra})
        elif category == "Dessert":
            menus["desserts"].append({"name": name, "price": price, "calorie": extra})

        # JSONへ保存
        with open(menus_path, "w", encoding="utf-8") as f:
            json.dump(menus, f, ensure_ascii=False, indent=2)

        flash(f"{category} に {name} を追加しました！")
        return redirect(url_for("admin"))

    return render_template("admin.html", menus=menus)
if __name__ == "__main__":
    app.run(debug=True,port=5001)