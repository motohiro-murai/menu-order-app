# app_gui.py
import os
import json
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timezone, timedelta

# 依存:
# - menu_item.py : Food / Drink / Dessert クラス
# - menu_io.py   : load_menus(), save_menus()
# 既存のCLI版(app.py)と同じ data/ フォルダを利用します。

from menu_item import Food, Drink, Dessert
from menu_io import load_menus, save_menus

# 共通保存先
DATA_DIR = "data"
HISTORY_FILE = os.path.join(DATA_DIR, "orders.json")
JST = timezone(timedelta(hours=9))

def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

def load_history_safely() -> list:
    ensure_data_dir()
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

def save_order_record(order_items):
    """order_items: list of (item_obj, qty)"""
    if not order_items:
        return False
    history = load_history_safely()
    record = {
        "timestamp": datetime.now(JST).isoformat(timespec="seconds"),
        "items": [
            {"name": it.name, "qty": qty, "price": getattr(it, "price", 0)}
            for it, qty in order_items
        ],
    }
    history.append(record)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    return True

def summarize(items):
    """items: list of item_obj（qtyぶん展開済みでOK）"""
    total_price   = sum(getattr(it, "price", 0) for it in items)
    total_calorie = sum(getattr(it, "calorie", 0) for it in items)
    total_volume  = sum(getattr(it, "volume_ml", 0) for it in items)
    total_sugar   = sum(getattr(it, "sugar_g", 0) for it in items)
    return total_price, total_calorie, total_volume, total_sugar

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("メニュー注文アプリ（GUI）")
        self.geometry("900x600")

        # データ
        self.foods, self.drinks, self.desserts = load_menus()
        self.catalog = {
            "Food": self.foods,
            "Drink": self.drinks,
            "Dessert": self.desserts,
        }
        self.cart = []  # list of (item, qty)

        # UI 構成
        self._build_menu_bar()
        self._build_main_panes()
        self._refresh_menu_list()
        self._update_totals()

    # ========= Menubar =========
    def _build_menu_bar(self):
        menubar = tk.Menu(self)
        menu_edit = tk.Menu(menubar, tearoff=False)
        menu_edit.add_command(label="メニューを追加…", command=self.cmd_add_item)
        menu_edit.add_command(label="メニューを削除…", command=self.cmd_delete_item)
        menu_edit.add_separator()
        menu_edit.add_command(label="メニューを再読み込み", command=self.cmd_reload_menus)
        menubar.add_cascade(label="編集", menu=menu_edit)

        menu_order = tk.Menu(menubar, tearoff=False)
        menu_order.add_command(label="注文を保存", command=self.cmd_save_order)
        menu_order.add_command(label="最新の注文履歴を表示", command=self.cmd_show_latest_history)
        menu_order.add_separator()
        menu_order.add_command(label="カートを空にする", command=self.cmd_clear_cart)
        menubar.add_cascade(label="注文", menu=menu_order)

        self.config(menu=menubar)

    # ========= Layout =========
    def _build_main_panes(self):
        root = ttk.Panedwindow(self, orient="horizontal")
        root.pack(fill="both", expand=True, padx=10, pady=(10,0))

        # 左ペイン: カテゴリ選択 + リスト + 数量 + 追加
        left = ttk.Frame(root)
        root.add(left, weight=1)

        self.category_var = tk.StringVar(value="Food")
        cat_row = ttk.Frame(left)
        cat_row.pack(fill="x", pady=(0,6))
        ttk.Label(cat_row, text="カテゴリ:").pack(side="left")
        ttk.OptionMenu(cat_row, self.category_var, "Food", "Food", "Drink", "Dessert",
                       command=lambda _: self._refresh_menu_list()).pack(side="left", padx=6)

        # 検索
        srch_row = ttk.Frame(left)
        srch_row.pack(fill="x", pady=(0,6))
        ttk.Label(srch_row, text="検索:").pack(side="left")
        self.search_var = tk.StringVar()
        ent = ttk.Entry(srch_row, textvariable=self.search_var)
        ent.pack(side="left", fill="x", expand=True, padx=6)
        ttk.Button(srch_row, text="クリア", command=lambda: (self.search_var.set(""), self._refresh_menu_list())).pack(side="left")
        self.search_var.trace_add("write", lambda *a: self._refresh_menu_list())

        # メニュー一覧
        self.menu_list = tk.Listbox(left, height=18)
        self.menu_list.pack(fill="both", expand=True)
        self.menu_list.bind("<Double-Button-1>", lambda e: self._add_selected_item())

        # 数量 + 追加ボタン
        qty_row = ttk.Frame(left)
        qty_row.pack(fill="x", pady=(6,0))
        ttk.Label(qty_row, text="数量:").pack(side="left")
        self.qty_var = tk.IntVar(value=1)
        qty = ttk.Spinbox(qty_row, from_=1, to=999, textvariable=self.qty_var, width=6)
        qty.pack(side="left")
        ttk.Button(qty_row, text="カートに追加", command=self._add_selected_item).pack(side="left", padx=8)

        # 右ペイン: カート（Treeview） + 操作
        right = ttk.Frame(root)
        root.add(right, weight=1)

        columns = ("name","price","qty","subtotal")
        self.cart_tv = ttk.Treeview(right, columns=columns, show="headings", height=18)
        for col, w in zip(columns, (280,80,60,100)):
            self.cart_tv.heading(col, text={"name":"商品名","price":"価格","qty":"数量","subtotal":"小計"}[col])
            self.cart_tv.column(col, width=w, anchor="center")
        self.cart_tv.pack(fill="both", expand=True)

        btn_row = ttk.Frame(right)
        btn_row.pack(fill="x", pady=(6,0))
        ttk.Button(btn_row, text="選択行を削除", command=self.cmd_remove_selected).pack(side="left")
        ttk.Button(btn_row, text="カートを空にする", command=self.cmd_clear_cart).pack(side="left", padx=6)
        ttk.Button(btn_row, text="注文を保存", command=self.cmd_save_order).pack(side="right")

        # ステータス(合計)
        self.status_var = tk.StringVar()
        bar = ttk.Label(self, textvariable=self.status_var, anchor="w", relief="groove")
        bar.pack(fill="x", padx=10, pady=10)

    # ========= Helpers =========
    def _filtered_items(self):
        cat = self.category_var.get()
        items = self.catalog.get(cat, [])
        q = self.search_var.get().strip()
        if not q:
            return items
        ql = q.lower()
        return [it for it in items if ql in it.name.lower() or ql in it.info().lower()]

    def _refresh_menu_list(self):
        self.menu_list.delete(0, "end")
        for it in self._filtered_items():
            self.menu_list.insert("end", it.info())

    def _add_selected_item(self):
        sel = self.menu_list.curselection()
        if not sel:
            messagebox.showinfo("情報", "メニューを選択してください。")
            return
        idx = sel[0]
        item = self._filtered_items()[idx]
        qty = self.qty_var.get()
        if qty <= 0:
            messagebox.showerror("エラー", "数量は1以上で入力してください。")
            return
        # 既存エントリ更新 or 追加
        for i, (it, q) in enumerate(self.cart):
            if it.name == item.name:
                self.cart[i] = (it, q + qty)
                break
        else:
            self.cart.append((item, qty))
        self._refresh_cart_view()
        self._update_totals()

    def _refresh_cart_view(self):
        self.cart_tv.delete(*self.cart_tv.get_children())
        for it, qty in self.cart:
            price = getattr(it, "price", 0)
            subtotal = price * qty
            self.cart_tv.insert("", "end", values=(it.name, price, qty, subtotal))

    def _update_totals(self):
        expanded = []
        for it, qty in self.cart:
            expanded.extend([it] * qty)
        price, cal, vol, sug = summarize(expanded)
        parts = [f"合計 金額: {price} 円"]
        if cal: parts.append(f"カロリー: {cal} kcal")
        if vol: parts.append(f"ドリンク量: {vol} ml")
        if sug: parts.append(f"糖質: {sug} g")
        self.status_var.set(" / ".join(parts) if parts else "カートは空です。")

    # ========= Commands =========
    def cmd_remove_selected(self):
        sel = self.cart_tv.selection()
        if not sel:
            return
        names = []
        for iid in sel:
            vals = self.cart_tv.item(iid, "values")
            if not vals:
                continue
            names.append(vals[0])
        if not names:
            return
        # remove from cart by name
        new_cart = []
        for it, qty in self.cart:
            if it.name not in names:
                new_cart.append((it, qty))
        self.cart = new_cart
        self._refresh_cart_view()
        self._update_totals()

    def cmd_clear_cart(self):
        if not self.cart:
            return
        if messagebox.askyesno("確認", "カートを空にしますか？"):
            self.cart.clear()
            self._refresh_cart_view()
            self._update_totals()

    def cmd_save_order(self):
        if not self.cart:
            messagebox.showinfo("情報", "カートが空です。")
            return
        if save_order_record(self.cart):
            messagebox.showinfo("保存", f"注文を保存しました。\n→ {HISTORY_FILE}")
            self.cart.clear()
            self._refresh_cart_view()
            self._update_totals()
        else:
            messagebox.showerror("エラー", "保存に失敗しました。")

    def cmd_show_latest_history(self):
        history = load_history_safely()
        if not history:
            messagebox.showinfo("履歴", "注文履歴はまだありません。")
            return
        latest = history[-1]
        ts = latest.get("timestamp", "-")
        lines = [f"日時: {ts}"]
        for it in latest.get("items", []):
            lines.append(f"{it.get('name','?')} × {it.get('qty','?')} (¥{it.get('price','?')})")
        messagebox.showinfo("最新の注文履歴", "\n".join(lines))

    def cmd_reload_menus(self):
        self.foods, self.drinks, self.desserts = load_menus()
        self.catalog = {
            "Food": self.foods,
            "Drink": self.drinks,
            "Dessert": self.desserts,
        }
        self._refresh_menu_list()
        messagebox.showinfo("情報", "メニューを再読み込みしました。")

    def cmd_add_item(self):
        # カテゴリ選択
        cat = self._ask_category()
        if not cat:
            return
        name = simpledialog.askstring("追加", "名前:")
        if not name:
            return
        price = self._ask_int("価格(円):", min_v=0)
        if price is None:
            return

        calorie = self._ask_opt_int("カロリー(kcal)［任意］:")
        volume  = self._ask_opt_int("容量(ml)［任意/Drink向け］:")
        sugar   = self._ask_opt_int("糖質(g)［任意］:")

        foods, drinks, desserts = self.foods, self.drinks, self.desserts
        if cat == "Food":
            foods.append(Food(name=name, price=price, calorie=calorie or 0))
        elif cat == "Drink":
            drinks.append(Drink(name=name, price=price, volume_ml=volume or 0, sugar_g=sugar or 0))
        else:
            desserts.append(Dessert(name=name, price=price, calorie=calorie or 0, sugar_g=sugar or 0))

        save_menus(foods, drinks, desserts)
        self.cmd_reload_menus()

    def cmd_delete_item(self):
        cat = self._ask_category()
        if not cat:
            return
        items = self.catalog.get(cat, [])
        if not items:
            messagebox.showinfo("情報", "このカテゴリには項目がありません。")
            return
        # 選択
        names = [it.name for it in items]
        idx = self._ask_from_list("削除する項目を選択", names)
        if idx is None:
            return
        removed = items.pop(idx)
        save_menus(self.foods, self.drinks, self.desserts)
        messagebox.showinfo("削除", f"削除しました: [{cat}] {removed.name}")
        self.cmd_reload_menus()

    # ========= Input helpers =========
    def _ask_category(self):
        dlg = SimpleListDialog(self, "カテゴリ選択", ["Food","Drink","Dessert"])
        self.wait_window(dlg)
        return dlg.result

    def _ask_from_list(self, title, options):
        dlg = SimpleListDialog(self, title, options)
        self.wait_window(dlg)
        if dlg.result is None:
            return None
        return dlg.index

    def _ask_int(self, prompt, min_v=None, max_v=None):
        while True:
            s = simpledialog.askstring("入力", prompt)
            if s is None:
                return None
            if s.isdigit():
                v = int(s)
                if (min_v is None or v >= min_v) and (max_v is None or v <= max_v):
                    return v
            messagebox.showerror("エラー", "整数で正しく入力してください。")

    def _ask_opt_int(self, prompt):
        s = simpledialog.askstring("入力", prompt + "（空Enterでスキップ）")
        if s in (None, ""):
            return None
        if s.isdigit():
            return int(s)
        messagebox.showerror("エラー", "整数で入力してください。")
        return None

class SimpleListDialog(tk.Toplevel):
    """一覧から1つ選ぶ簡易ダイアログ"""
    def __init__(self, master, title, options):
        super().__init__(master)
        self.title(title)
        self.resizable(False, False)
        self.result = None
        self.index = None

        frm = ttk.Frame(self, padding=12)
        frm.pack(fill="both", expand=True)

        self.lb = tk.Listbox(frm, height=min(12, len(options)))
        for opt in options:
            self.lb.insert("end", opt)
        self.lb.pack(fill="both", expand=True)

        btns = ttk.Frame(frm)
        btns.pack(fill="x", pady=(8,0))
        ttk.Button(btns, text="OK", command=self._ok).pack(side="right")
        ttk.Button(btns, text="キャンセル", command=self._cancel).pack(side="right", padx=6)

        self.lb.bind("<Double-Button-1>", lambda e: self._ok())
        self.grab_set()
        self.transient(master)
        self.lb.focus_set()

    def _ok(self):
        sel = self.lb.curselection()
        if not sel:
            self.result = None
        else:
            self.index = sel[0]
            self.result = self.lb.get(sel[0])
        self.destroy()

    def _cancel(self):
        self.result = None
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()
