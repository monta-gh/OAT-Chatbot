import streamlit as st
import openai
import os

# 環境変数からAPIキーを取得
api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = api_key

# 日本語から英語への翻訳
def translate_to_english(japanese_text):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",  # 使用するモデル
        messages=[{"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": f"Translate the following Japanese text to English: {japanese_text}"}],
        temperature=0.7
    )
    translation = response['choices'][0]['message']['content']
    return translation

# Webアプリのインターフェース
def main():
    st.title("日英翻訳 Webアプリ")
    
    # ユーザーからの日本語入力を受け取る
    japanese_text = st.text_area("日本語のテキストを入力してください:")

    if japanese_text:
        st.write("翻訳結果:")
        # 翻訳を実行
        translation = translate_to_english(japanese_text)
        st.write(translation)

# Streamlitアプリを実行するためのメイン関数
if __name__ == "__main__":
    main()
