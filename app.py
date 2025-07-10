from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime, timedelta
import os

# Flaskアプリの設定（static_folderでフロントの位置を指定）
app = Flask(__name__, static_folder="frontend")

# 入場管理パラメータ
MAX_ACTIVE = 2500
MAX_DIRECT = 50
BATCH_SIZE = 25
REDIRECT_URL = "https://growsyncer-1-0-2.onrender.com/client/"  # 遷移先URL
TIMEOUT_MINUTES = 10

# 状態管理
active_users = {}        # user_id: 入場時間
waiting_queue = []       # user_id順

# ✅ "/" にアクセスされたとき index.html を返す

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

# ✅ その他静的ファイル（JSやCSS）を配信
@app.route("/<path:filename>")
def serve_static_files(filename):
    file_path = os.path.join(app.static_folder, filename)
    if os.path.exists(file_path):
        return send_from_directory(app.static_folder, filename)
    return f"{filename} が見つかりません", 404

# ✅ 状態を初期化（開発用）
@app.route("/reset")
def reset():
    active_users.clear()
    waiting_queue.clear()
    return "状態が初期化されました", 200

# ⏱ 古いアクティブユーザーを削除
def cleanup_active_users():
    now = datetime.now()
    expired = [uid for uid, t in active_users.items() if now - t > timedelta(minutes=TIMEOUT_MINUTES)]
    for uid in expired:
        del active_users[uid]

# 🎯 入場判定処理
@app.route("/access")
def access_handler():
    cleanup_active_users()
    user_id = request.remote_addr  # 実運用では UUIDやCookie推奨

    # ① すでに入場済みのユーザーは即リダイレクト
    if user_id in active_users:
        return jsonify({"redirectUrl": REDIRECT_URL})

    # ② 入場枠が空いている → 即入場
    if len(active_users) < MAX_DIRECT:
        active_users[user_id] = datetime.now()
        return jsonify({"redirectUrl": REDIRECT_URL})

    # ③ 順番待ちに追加（未登録の場合のみ）
    if user_id not in waiting_queue:
        waiting_queue.append(user_id)

    # ④ バッチ処理（25人以上待ち、かつMAX_ACTIVE未満）
    if len(waiting_queue) >= BATCH_SIZE and len(active_users) + BATCH_SIZE <= MAX_ACTIVE:
        batch = waiting_queue[:BATCH_SIZE]
        for uid in batch:
            active_users[uid] = datetime.now()
        waiting_queue[:] = waiting_queue[BATCH_SIZE:]
        if user_id in batch:
            return jsonify({"redirectUrl": REDIRECT_URL})

    # ⑤ 順番待ちの位置を返す
    if user_id in waiting_queue:
        position = waiting_queue.index(user_id) + 1
        return jsonify({"waitNumber": position})

    # ⑥ 想定外の処理（セーフガード）
    return jsonify({"waitNumber": 2000})


if __name__ == "__main__":
    print("Flaskサーバー起動中... http://localhost:5000/")
    app.run(debug=True)




