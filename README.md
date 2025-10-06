
# メニューオーダーアプリ 🍴

Pythonで作成したシンプルな **メニュー注文管理アプリ** です。  
フード / ドリンク / デザートを選んで、合計金額やカロリーを自動計算できます。  
JSONを使ったメニュー保存や拡張も可能です。

---

## 📸 サンプル画面
（スクリーンショットをここに貼る予定）

---

## 🚀 機能
- メニューから複数商品を選択して注文
- 合計金額・カロリーの自動計算
- メニューをJSON形式で保存・読み込み
- CLI形式で操作可能
- GUI対応

---

## 🛠 使用技術
- Python 3.13
- JSONファイル入出力
- argparse（コマンドライン引数）
- Tkinter（GUI化を検討中）

---

## ▶️ 使い方

### インストール
```bash
git clone https://github.com/motohiro-murai/menu-order-app.git
```


cd menu-order-app

### 実行例
```bash
# フードを追加
python app.py add food "ハンバーグ" 800 500

# ドリンクを追加
python app.py add drink "コーヒー" 300 10

# デザートを追加
python app.py add dessert "チーズケーキ" 600 350

# 注文実行（まとめて注文）
python app.py order ハンバーグ コーヒー チーズケーキ


menu-order-app/
├── app.py          # エントリポイント
├── menu_item.py    # Food/Drink/Dessertクラス
├── menu_io.py      # JSON入出力処理
├── data/
│   └── menus.json  # 保存されるメニュー
└── README.md

