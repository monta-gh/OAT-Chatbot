from flask import Flask, render_template, request, session, redirect, url_for
import os
from chatbot_prompt_module import process_query

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "your_secret_key")  # セッション管理用

@app.route("/", methods=["GET", "POST"])
def index():
    answer = ""
    question = ""
    search_results = None
    keywords = []
    if request.method == "POST":
        question = request.form["question"]
        result = process_query(question, show_all_results=False)
        answer = result["answer"]
        search_results = result["search_results"]
        keywords = result["keywords"]

        # 履歴に追加（最新を上に、ただし最新の質問は次回の表示で履歴に）
        history = session.get("chat_history", [])
        history.insert(0, {
            "question": question,
            "answer": answer,
            "keywords": keywords,
            "vector_results": search_results["vector_results"],
            "keyword_results_html": search_results["keyword_results_html"]
        })
        session["chat_history"] = history[:10]  # 履歴を10件に制限

    return render_template("index.html", 
                         answer=answer, 
                         question=question, 
                         search_results=search_results, 
                         keywords=keywords,
                         history=session.get("chat_history", [])[1:])  # 最新の質問を履歴から除外

@app.route("/clear", methods=["POST"])
def clear_history():
    session.pop("chat_history", None)
    return redirect(url_for("index"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)