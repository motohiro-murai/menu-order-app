# 🍴 メニュー注文アプリ（Menu Order App）

Flaskで作成したシンプルな **メニュー注文Webアプリ** です。  
フード / ドリンク / デザートを選んで、合計金額やカロリーを自動計算できます。  
JSONを使ったメニュー保存や、管理ページからの追加編集にも対応しています。

---

## 🚀 主な機能
- メニューから複数商品を選択して注文  
- カート機能（追加・削除・数量変更）  
- 注文履歴を `orders.json` に保存  
- 管理ページ `/admin` でメニューを追加可能  
- JSONを使ったデータ管理  
- カフェ風デザイン ☕  

---

## 🛠 使用技術
- Python 3.13  
- Flask 3.1.2  
- HTML / CSS（Jinja2 Templates）  
- JSONファイル入出力  

---

## ▶️ 実行方法

### ◎ 仮想環境の作成と起動
```bash
python3 -m venv .venv
source .venv/bin/activate
```




### ② Flaskのインストール
pip install flask

###③ アプリの起動
python app_web.py

###④ ブラウザでアクセス

http://127.0.0.1:5001

（管理ページ）http://127.0.0.1:5001/admin


ディレクトリ構成
menu-order-app/
├── app_web.py           # Flaskアプリ本体
├── menu_io.py           # JSON入出力処理
├── menu_item.py         # Food/Drink/Dessertクラス定義
├── data/
│   ├── menus.json       # メニュー情報
│   └── orders.json      # 注文履歴
├── static/
│   └── style.css        # デザインCSS
├── templates/           # HTMLテンプレート
│   ├── base.html
│   ├── menu.html
│   ├── cart.html
│   ├── order_complete.html
│   └── admin.html
└── README.md
