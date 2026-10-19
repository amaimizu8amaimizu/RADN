
import streamlit as st
import feedparser
import requests

st.title("RADNの箱")

# --------------------------------------------------
# Bluesky 投稿取得用関数
# --------------------------------------------------
def get_bluesky_posts(query, limit=5):
    url = "https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts"
    params = {"q": query, "limit": limit}
    posts = []
    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            for item in data.get("posts", []):
                record = item.get("record", {})
                author = item.get("author", {})
                
                uri_parts = item.get("uri", "").split("/")
                rkey = uri_parts[-1] if uri_parts else ""
                handle = author.get("handle", "")
                post_url = f"https://bsky.app/profile/{handle}/post/{rkey}" if handle and rkey else "#"

                posts.append({
                    "text": record.get("text", ""),
                    "author": author.get("displayName") or handle,
                    "handle": handle,
                    "url": post_url
                })
    except Exception as e:
        st.error(f"Blueskyのデータ取得エラー: {e}")
    return posts


# 1. 🎬 名画座・クラシック映画 上映情報（Bluesky検索）
st.header("🎬 旧作・名画座 上映情報")
movie_classic_posts = get_bluesky_posts("名画座 OR リバイバル上映 OR 午前10時の映画祭 OR 旧作上映", limit=5)
for p in movie_classic_posts:
    st.markdown(f"**{p['author']}** (`@{p['handle']}`)")
    st.write(p["text"])
    st.markdown(f'<a href="{p["url"]}" target="_blank" rel="noopener noreferrer">Blueskyで見る</a>', unsafe_allow_html=True)
    st.write("---")

# 2. 🍿 映画コラム・感想（Bluesky検索）
st.header("🍿 映画コラム・クラシック映画の話題")
movie_review_posts = get_bluesky_posts("映画 考察 OR 映画 レビュー OR シネマカリテ OR ル・シネマ", limit=5)
for p in movie_review_posts:
    st.markdown(f"**{p['author']}** (`@{p['handle']}`)")
    st.write(p["text"])
    st.markdown(f'<a href="{p["url"]}" target="_blank" rel="noopener noreferrer">Blueskyで見る</a>', unsafe_allow_html=True)
    st.write("---")

# 3. 🎨 ヒグチユウコ 最新の話題（Bluesky検索）
st.header("🎨 ヒグチユウコ 最新情報")
higuchi_posts = get_bluesky_posts("ヒグチユウコ", limit=5)
for p in higuchi_posts:
    st.markdown(f"**{p['author']}** (`@{p['handle']}`)")
    st.write(p["text"])
    st.markdown(f'<a href="{p["url"]}" target="_blank" rel="noopener noreferrer">Blueskyで見る</a>', unsafe_allow_html=True)
    st.write("---")

# 4. 🐱 猫（Bluesky検索）
st.header("🐾 猫の話題")
cat_posts = get_bluesky_posts("猫", limit=5)
for p in cat_posts:
    st.markdown(f"**{p['author']}** (`@{p['handle']}`)")
    st.write(p["text"])
    st.markdown(f'<a href="{p["url"]}" target="_blank" rel="noopener noreferrer">Blueskyで見る</a>', unsafe_allow_html=True)
    st.write("---")

# 5. 🌵 多肉植物（Bluesky検索）
st.header("🌵 多肉植物")
succulent_posts = get_bluesky_posts("多肉植物", limit=5)
for p in succulent_posts:
    st.markdown(f"**{p['author']}** (`@{p['handle']}`)")
    st.write(p["text"])
    st.markdown(f'<a href="{p["url"]}" target="_blank" rel="noopener noreferrer">Blueskyで見る</a>', unsafe_allow_html=True)
    st.write("---")

# 6. 本日の猫ちゃん（ランダム画像）
st.header("📷 本日の猫ちゃん")
st.image("https://cataas.com/cat", caption="リロードするたびに違う猫が出ます！", use_container_width=True)
# 8. 本日の猫ちゃん
st.header("🐾 本日の猫ちゃん")
st.image("https://cataas.com/cat", caption="リロードするたびに違う猫が出ます！", use_container_width=True)
