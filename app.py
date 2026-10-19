
import streamlit as st
import feedparser
import requests

st.title("🎬 My Cinema & Life Hub")

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


# 1. 映画ニュース・上映情報
st.header("映画ニュース・上映情報")
feed = feedparser.parse('https://eiga.com/news/feed/')
for entry in feed.entries[:5]:
    st.markdown(f'• <a href="{entry.link}" target="_blank" rel="noopener noreferrer">**{entry.title}**</a>', unsafe_allow_html=True)
    st.write("---")

st.write("※後ほどここに、シネマカリテやル・シネマなど名小座の更新情報も追加できます。")
st.write("---")

# 2. 映画コラム・SNS
st.header("映画コラム・SNS")
st.write("エリオ・ペルティ監督のようなマニアックな作品の解説や、お気に入りの映画評論家の更新をここにまとめます。")
st.write("🍿 **ピックアップ記事**")
feed_note = feedparser.parse('https://note.com/topic/cinema/rss')
for entry in feed_note.entries[:5]:
    st.markdown(f'• <a href="{entry.link}" target="_blank" rel="noopener noreferrer">{entry.title}</a>', unsafe_allow_html=True)
    st.write("---")

# 3. 話題のニュース
st.header("話題のニュース")
feed_hatebu = feedparser.parse('https://b.hatena.ne.jp/hotentry/entertainment.rss')
for entry in feed_hatebu.entries[:5]:
    st.markdown(f'• <a href="{entry.link}" target="_blank" rel="noopener noreferrer">{entry.title}</a>', unsafe_allow_html=True)
    st.write("---")

# 4. Bluesky：猫
st.header("🦋 Bluesky：猫")
cat_posts = get_bluesky_posts("猫", limit=5)
for p in cat_posts:
    st.markdown(f"**{p['author']}** (`@{p['handle']}`)")
    st.write(p["text"])
    st.markdown(f'<a href="{p["url"]}" target="_blank" rel="noopener noreferrer">Blueskyで見る</a>', unsafe_allow_html=True)
    st.write("---")

# 5. Bluesky：多肉植物
st.header("🦋 Bluesky：多肉植物")
succulent_posts = get_bluesky_posts("多肉植物", limit=5)
for p in succulent_posts:
    st.markdown(f"**{p['author']}** (`@{p['handle']}`)")
    st.write(p["text"])
    st.markdown(f'<a href="{p["url"]}" target="_blank" rel="noopener noreferrer">Blueskyで見る</a>', unsafe_allow_html=True)
    st.write("---")

# 6. Bluesky：これから上映する映画
st.header("🦋 Bluesky：これから上映する映画")
movie_posts = get_bluesky_posts("これから上映する映画 OR 公開予定 映画", limit=5)
for p in movie_posts:
    st.markdown(f"**{p['author']}** (`@{p['handle']}`)")
    st.write(p["text"])
    st.markdown(f'<a href="{p["url"]}" target="_blank" rel="noopener noreferrer">Blueskyで見る</a>', unsafe_allow_html=True)
    st.write("---")

# 7. ヒグチユウコ 最新情報
st.header("ヒグチユウコ 最新情報")
st.markdown('• <a href="https://higuchiyuko.tokyo/" target="_blank" rel="noopener noreferrer">公式サイトのNEWS: HIGUCHI YUKO Official Website</a>', unsafe_allow_html=True)
st.write("---")

# 8. 本日の猫ちゃん
st.header("🐾 本日の猫ちゃん")
st.image("https://cataas.com/cat", caption="リロードするたびに違う猫が出ます！", use_container_width=True)
