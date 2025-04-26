from flask import Flask, render_template, request, session, redirect, url_for
import os
from chatbot_prompt_module import get_chat_response

app = Flask(__name__)

# ベーシック認証用関数
def check_auth(username, password):
    env_user = os.getenv("BASIC_AUTH_USERNAME")
    env_pass = os.getenv("BASIC_AUTH_PASSWORD")
    return username == env_user and password == env_pass

def authenticate():
    from flask import Response
    return Response(
        'ログインが必要です', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

app.secret_key = os.getenv("FLASK_SECRET_KEY", "your_secret_key")  # セッション管理用

@app.before_request
def require_authentication():
    from flask import request
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()

@app.route("/", methods=["GET", "POST"])
def index():
    answer = ""
    question = ""
    if request.method == "POST":
        question = request.form["question"]
        answer = get_chat_response(question)

        # 履歴に追加（最新を上に）
        history = session.get("chat_history", [])
        history.insert(0, {"question": question, "answer": answer})
        session["chat_history"] = history

    return render_template("index.html", answer=answer, question=question, history=session.get("chat_history", []))

# 🧹 履歴クリア用ルート
@app.route("/clear", methods=["POST"])
def clear_history():
    session.pop("chat_history", None)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
