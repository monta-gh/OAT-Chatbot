# chatbot_prompt_module.py
import pandas as pd
import openai
import os
from janome.tokenizer import Tokenizer

openai.api_key = os.getenv("OPENAI_API_KEY")

csv_path = "blog_list_analyzed.csv"
df = pd.read_csv(csv_path)

NG_WORDS = {'する', 'ある', 'こと', 'いる', 'なる', 'そして', 'また', 'いい', '思う'}
tokenizer = Tokenizer()

def extract_keywords(text):
    tokens = tokenizer.tokenize(text)
    return [
        token.base_form
        for token in tokens
        if token.part_of_speech.split(',')[0] in ['名詞', '動詞', '形容詞']
        and token.base_form not in NG_WORDS
    ]

def get_chat_response(user_input):
    keywords = extract_keywords(user_input)
    results = df[
        df['analyzed_content'].apply(lambda x: any(k in str(x) for k in keywords)) |
        df['title'].apply(lambda x: any(k in str(x) for k in keywords))
    ]

    if results.empty:
        results = df[['title', 'analyzed_content', 'personality_hint']].sample(n=min(2, len(df)), random_state=None)
    else:
        results = results[['title', 'analyzed_content', 'personality_hint']].sample(n=min(2, len(results)), random_state=None)

    references = ""
    for _, row in results.iterrows():
        references += f"\n【タイトル】: {row['title']}\n【要約】: {row['analyzed_content']}\n"

    prompt = f"""
You are an assistant who acts like the author of this blog.
The author is a dedicated and passionate therapist who cares deeply for patients, is driven by curiosity, pursues growth through self-reflection, and supports the progress of others.
The author developed a therapeutic method called "OAT (Ogawa Acupuncture Therapy)", which combines acupuncture and individualized holistic care.
Below are representative summaries extracted from the author's blog posts.
Use this information to answer the user's question in a warm and thoughtful manner, as the author would, in Japanese.

[User's Question]
{user_input}

[Reference Information]
{references}
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "あなたはOATブログの著者のように話すアシスタントです。"},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message["content"].strip()
