import streamlit as st
import feedparser
import requests
import urllib.parse

st.title("🎬 My Cinema & Life Hub")

# --------------------------------------------------
# Bluesky 投稿取得用関数
# --------------------------------------------------
def get_bluesky_posts(query, limit=3):
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

# --------------------------------------------------
# Googleニュース RSS取得用関数
# --------------------------------------------------
def get_google_news(query, limit=3):
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ja&gl=JP&ceid=JP:ja"
    feed = feedparser.parse(rss_url)
    return feed.entries[:limit]


# ==================================================
# 1. 🎬 旧作・名画座・映画の上映情報
# ==================================================
st.header("🎬 旧作・名画座 上映情報")

st.subheader("📰 ニュース・Web記事")
movie_news = get_google_news("名画座 OR リバイバル上映 OR 午前10時の映画祭", limit=3)
for entry in movie_news:
    st.markdown(f'• <a href="{entry.link}" target="_blank" rel="noopener noreferrer">**{entry.title}**</a>', unsafe_allow_html=True)

st.subheader("🦋 Blueskyでの話題")
movie_posts = get_bluesky_posts("名画座 OR リバイバル上映 OR 午前10時の映画祭 OR 旧作上映", limit=3)
for p in movie_posts:
    st.markdown(f"**{p['author']}** (`@{p['handle']}`)")
    st.write(p["text"])
    st.markdown(f'<a href="{p["url"]}" target="_blank" rel="noopener noreferrer">Blueskyで見る</a>', unsafe_allow_html=True)
    st.write("---")

st.write("---")


# ==================================================
# 2. 🎨 ヒグチユウコ 最新情報
# ==================================================
st.header("🎨 ヒグチユウコ 最新情報")

st.subheader("📰 ニュース・関連Web記事")
higuchi_news = get_google_news("ヒグチユウコ", limit=3)
for entry in higuchi_news:
    st.markdown(f'• <a href="{entry.link}" target="_blank" rel="noopener noreferrer">**{entry.title}**</a>', unsafe_allow_html=True)

st.subheader("🦋 Blueskyでの話題")
higuchi_posts = get_bluesky_posts("ヒグチユウコ", limit=3)
for p in higuchi_posts:
    st.markdown(f"**{p['author']}** (`@{p['handle']}`)")
    st.write(p["text"])
    st.markdown(f'<a href="{p["url"]}" target="_blank" rel="noopener noreferrer">Blueskyで見る</a>', unsafe_allow_html=True)
    st.write("---")

st.write("---")


# ==================================================
# 3. 🐾 猫の話題
# ==================================================
st.header("🐾 猫の話題")

st.subheader("📰 猫のニュース・記事")
cat_news = get_google_news("猫 話題 OR 保護猫", limit=3)
for entry in cat_news:
    st.markdown(f'• <a href="{entry.link}" target="_blank" rel="noopener noreferrer">**{entry.title}**</a>', unsafe_allow_html=True)

st.subheader("🦋 Blueskyの投稿")
cat_posts = get_bluesky_posts("猫", limit=3)
for p in cat_posts:
    st.markdown(f"**{p['author']}** (`@{p['handle']}`)")
    st.write(p["text"])
    st.markdown(f'<a href="{p["url"]}" target="_blank" rel="noopener noreferrer">Blueskyで見る</a>', unsafe_allow_html=True)
    st.write("---")

st.write("---")


# ==================================================
# 4. 🌵 多肉植物
# ==================================================
st.header("🌵 多肉植物")

st.subheader("📰 多肉植物のニュース・記事")
succulent_news = get_google_news("多肉植物", limit=3)
for entry in succulent_news:
    st.markdown(f'• <a href="{entry.link}" target="_blank" rel="noopener noreferrer">**{entry.title}**</a>', unsafe_allow_html=True)

st.subheader("🦋 Blueskyの投稿")
succulent_posts = get_bluesky_posts("多肉植物", limit=3)
for p in succulent_posts:
    st.markdown(f"**{p['author']}** (`@{p['handle']}`)")
    st.write(p["text"])
    st.markdown(f'<a href="{p["url"]}" target="_blank" rel="noopener noreferrer">Blueskyで見る</a>', unsafe_allow_html=True)
    st.write("---")

st.write("---")


# ==================================================
# 5. 📷 本日の猫ちゃん（ランダム画像）
# ==================================================
st.header("📷 本日の猫ちゃん")
st.image("https://cataas.com/cat", caption="リロードするたびに違う猫が出ます！", use_container_width=True)
