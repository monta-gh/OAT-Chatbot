import os
import re
from janome.tokenizer import Tokenizer
import openai
import chromadb

# 初期設定
openai.api_key = os.getenv("OPENAI_API_KEY")
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_collection(name="blog_articles")
EMBED_MODEL = "text-embedding-3-small"

def get_query_embedding(text):
    response = openai.Embedding.create(model=EMBED_MODEL, input=text)
    return response["data"][0]["embedding"]

def generate_answer(context, query):
    prompt = (
        f"以下はブログ記事の内容です。\n\n{context}\n\n"
        f"質問に対し、記事の内容だけを使い、140～170文字以内で答えてください。\n"
        f"情報がない場合はその旨を伝えてください。\n\n質問: {query}"
    )
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "親切で正確なアシスタント"},
            {"role": "user", "content": prompt}
        ],
        max_tokens=175
    )
    return response.choices[0].message["content"]

def preprocess_query(query):
    t = Tokenizer()
    keywords = [token.surface for token in t.tokenize(query) if token.part_of_speech.startswith('名詞')]
    stop_words = ["とは", "何か", "について", "の", "記事", "言葉", "ありますか"]
    keywords = [kw for kw in keywords if kw not in stop_words and len(kw) > 1]
    alpha_keywords = re.findall(r'\b[A-Z]{2,}\b', query)
    keywords.extend(alpha_keywords)
    synonyms = {
        "呼吸": ["breath", "呼吸法", "深呼吸"],
        "治療": ["療法", "施術", "治療法"],
        "ABT": ["ABT-2", "ABT2"]
    }
    expanded_keywords = []
    for kw in keywords:
        expanded_keywords.append(kw)
        if kw in synonyms:
            expanded_keywords.extend(synonyms[kw])
    return expanded_keywords if expanded_keywords else [query.strip()]

def keyword_search(keywords, documents, metadatas):
    matched_results = []
    for i, doc in enumerate(documents):
        matches = 0
        matched_keywords = set()
        for keyword in keywords:
            pattern = re.escape(keyword)
            if keyword.upper() == "ABT":
                pattern = r'\bABT(?:-?\d)?\b'
            if re.search(pattern, doc, re.IGNORECASE) and keyword not in matched_keywords:
                matches += 1
                matched_keywords.add(keyword)
        if matches > 0:
            matched_results.append((doc, metadatas[i], matches))
    matched_results.sort(key=lambda x: x[2], reverse=True)
    return [(doc, meta, matches) for doc, meta, matches in matched_results[:20]]

def generate_keyword_results_html(keyword_matches):
    if not keyword_matches:
        return "<p>🔍 キーワード検索結果なし。</p>"
    initial_display = 4
    html = "<div>\n<h3>🔍 キーワード検索結果:</h3>\n<ul id='keyword-results-initial'>\n"
    for i, (doc, meta, matches) in enumerate(keyword_matches[:initial_display]):
        html += f"<li>{i+1}. {meta.get('title', 'N/A')}（キーワード一致：{matches}）<br>URL: <a href='{meta.get('url', 'N/A')}' target='_blank'>{meta.get('url', 'N/A')}</a></li>\n"
    html += "</ul>\n"
    if len(keyword_matches) > initial_display:
        html += "<div id='keyword-results-more' style='display: none;'>\n<ul>\n"
        for i, (doc, meta, matches) in enumerate(keyword_matches[initial_display:]):
            html += f"<li>{i+1+initial_display}. {meta.get('title', 'N/A')}（キーワード一致：{matches}）<br>URL: <a href='{meta.get('url', 'N/A')}' target='_blank'>{meta.get('url', 'N/A')}</a></li>\n"
        html += "</ul>\n</div>\n"
        html += "<button onclick='showMoreResults()'>もっと見る</button>\n"
    html += "</div>\n"
    html += """
    <script>
    function showMoreResults() {
        document.getElementById('keyword-results-more').style.display = 'block';
        document.querySelector('button[onclick="showMoreResults()"]').style.display = 'none';
    }
    </script>
    """
    return html

def get_search_results(vector_results, keyword_matches, limit=4):
    vector_results_formatted = []
    if vector_results["documents"]:
        for i in range(min(3, len(vector_results["documents"][0]))):
            meta = vector_results["metadatas"][0][i]
            dist = vector_results["distances"][0][i]
            if dist <= 0.85:
                vector_results_formatted.append({
                    "title": meta.get("title", "N/A"),
                    "url": meta.get("url", "N/A"),
                    "distance": f"{dist:.4f}"
                })
            if len(vector_results_formatted) >= 3:
                break
    keyword_results_formatted = []
    for doc, meta, matches in keyword_matches:
        keyword_results_formatted.append({
            "title": meta.get("title", "N/A"),
            "url": meta.get("url", "N/A"),
            "matches": matches
        })
    total_keyword_matches = len(keyword_matches)
    limited_keyword_matches = keyword_results_formatted[:limit]
    keyword_results_html = generate_keyword_results_html(keyword_matches)
    return {
        "vector_results": vector_results_formatted,
        "keyword_results": limited_keyword_matches,
        "keyword_results_html": keyword_results_html,
        "total_keyword_matches": total_keyword_matches,
        "has_more": total_keyword_matches > limit
    }

def process_query(query, show_all_results=False):
    keywords = preprocess_query(query)
    embedding = get_query_embedding(query)
    results = collection.query(query_embeddings=[embedding], n_results=5)
    all_documents = collection.get()["documents"]
    all_metadatas = collection.get()["metadatas"]
    keyword_matches = keyword_search(keywords, all_documents, all_metadatas)
    short_context_parts = []
    if results["documents"]:
        for i in range(min(2, len(results["documents"][0]))):
            doc = results["documents"][0][i]
            short_context_parts.append(doc[:300])
    if keyword_matches:
        for doc, _, _ in keyword_matches:
            if doc not in short_context_parts:
                short_context_parts.append(doc[:300])
    short_context = "\n---\n".join(short_context_parts[:2]) if short_context_parts else ""
    if short_context and not any(keyword in short_context for keyword in keywords):
        for i in range(min(3, len(results["documents"][0]))):
            doc = results["documents"][0][i]
            if doc not in short_context_parts:
                short_context_parts.append(doc[:300])
                break
        short_context = "\n---\n".join(short_context_parts[:2]) if short_context_parts else ""
    answer = None
    if short_context:
        answer = generate_answer(short_context, query)
    search_results = get_search_results(results, keyword_matches)
    return {
        "answer": answer,
        "context": short_context,
        "search_results": search_results,
        "keywords": keywords,
        "keyword_matches": keyword_matches
    }