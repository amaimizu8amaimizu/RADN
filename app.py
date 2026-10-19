import streamlit as st
import feedparser
import requests
import urllib.parse
import re

st.set_page_config(page_title="My Cinema & Life Hub", layout="wide")

st.title("🎬 My Cinema & Life Hub")

# --------------------------------------------------
# 補助関数：Bluesky 投稿取得（検索ロジック改善版）
# --------------------------------------------------
def get_bluesky_posts(query, limit=3):
    url = "https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts"
    params = {"q": query, "limit": limit}
    posts = []
    try:
        res = requests.get(url, params=params, timeout=5)
        if res.status_code == 200:
            data = res.json()
            for item in data.get("posts", []):
                record = item.get("record", {})
                author = item.get("author", {})
                uri_parts = item.get("uri", "").split("/")
                rkey = uri_parts[-1] if uri_parts else ""
                handle = author.get("handle", "")
                post_url = f"https://bsky.app/profile/{handle}/post/{rkey}" if handle and rkey else "#"
                
                embed = item.get("embed", {})
                img_url = None
                if "images" in embed and len(embed["images"]) > 0:
                    img_url = embed["images"][0].get("fullsize")

                posts.append({
                    "text": record.get("text", ""),
                    "author": author.get("displayName") or handle,
                    "handle": handle,
                    "url": post_url,
                    "image": img_url
                })
    except Exception as e:
        pass
    return posts

# --------------------------------------------------
# 補助関数：Googleニュース取得（サムネイル付き）
# --------------------------------------------------
def get_google_news(query, limit=3):
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ja&gl=JP&ceid=JP:ja"
    feed = feedparser.parse(rss_url)
    articles = []
    for entry in feed.entries[:limit]:
        img_url = None
        if "summary" in entry:
            match = re.search(r'src="([^"]+)"', entry.summary)
            if match:
                img_url = match.group(1)
        articles.append({
            "title": entry.title,
            "link": entry.link,
            "image": img_url
        })
    return articles

# --------------------------------------------------
# 補助関数：Note記事取得（アイキャッチ画像付き）
# --------------------------------------------------
def get_note_posts(keyword, limit=3):
    encoded_kw = urllib.parse.quote(keyword)
    rss_url = f"https://note.com/hashtag/{encoded_kw}/rss"
    feed = feedparser.parse(rss_url)
    posts = []
    for entry in feed.entries[:limit]:
        img_url = None
        if hasattr(entry, 'media_thumbnail') and len(entry.media_thumbnail) > 0:
            img_url = entry.media_thumbnail[0]['url']
        elif 'enclosures' in entry and len(entry.enclosures) > 0:
            img_url = entry.enclosures[0]['href']
        
        posts.append({
            "title": entry.title,
            "link": entry.link,
            "image": img_url
        })
    return posts

# --------------------------------------------------
# 補助関数：Reddit写真・投稿取得
# --------------------------------------------------
def get_reddit_posts(subreddit, limit=3):
    url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit+2}"
    headers = {"User-Agent": "Mozilla/5.0"}
    posts = []
    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            data = res.json()
            for child in data.get("data", {}).get("children", []):
                pdata = child.get("data", {})
                if pdata.get("stickied"):
                    continue
                img_url = pdata.get("url", "")
                if not any(img_url.endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".gif"]):
                    img_url = None
                posts.append({
                    "title": pdata.get("title", ""),
                    "permalink": f"https://reddit.com{pdata.get('permalink')}",
                    "image": img_url
                })
                if len(posts) >= limit:
                    break
    except Exception:
        pass
    return posts

# --------------------------------------------------
# 表示用共通関数（画像付きカード描画）
# --------------------------------------------------
def render_card_list(items):
    if not items:
        st.caption("※該当する投稿が見つかりませんでした。")
        st.write("---")
        return
        
    for item in items:
        col1, col2 = st.columns([1, 3])
        with col1:
            if item.get("image"):
                st.image(item["image"], use_container_width=True)
            else:
                st.markdown("🖼️ *(画像なし)*")
        with col2:
            title = item.get("title") or item.get("text") or ""
            link = item.get("link") or item.get("url") or item.get("permalink") or "#"
            st.markdown(f'<a href="{link}" target="_blank" rel="noopener noreferrer">**{title}**</a>', unsafe_allow_html=True)
            if item.get("author"):
                st.caption(f"by {item['author']}")
        st.write("---")


# ==================================================
# 1. 🎬 旧作・名画座・映画の上映情報
# ==================================================
st.header("🎬 旧作・名画座 上映情報 & 映画コラム")

st.subheader("📰 Googleニュース")
render_card_list(get_google_news("名画座", limit=3))

st.subheader("📝 Note (映画感想・コラム)")
render_card_list(get_note_posts("映画鑑賞", limit=3))

st.subheader("🦋 Blueskyでの話題")
render_card_list(get_bluesky_posts("名画座", limit=3))


# ==================================================
# 2. 🏛️ 美術館・博物館の展示情報
# ==================================================
st.header("🏛️ 美術館・博物館 展示情報")

st.subheader("📰 展覧会ニュース")
render_card_list(get_google_news("特別展", limit=3))

st.subheader("📝 Note (美術展レポート)")
render_card_list(get_note_posts("美術展", limit=3))


# ==================================================
# 3. ⛩️ 御朱印 情報
# ==================================================
st.header("⛩️ 御朱印・神社仏閣 情報")

st.subheader("📰 御朱印ニュース")
render_card_list(get_google_news("御朱印", limit=3))

st.subheader("📝 Note (御朱印巡りレポ)")
render_card_list(get_note_posts("御朱印", limit=3))

st.subheader("🦋 Blueskyの投稿")
render_card_list(get_bluesky_posts("御朱印", limit=3))


# ==================================================
# 4. 🎨 ヒグチユウコ 最新情報
# ==================================================
st.header("🎨 ヒグチユウコ 最新情報")

st.subheader("📰 ニュース & Web記事")
render_card_list(get_google_news("ヒグチユウコ", limit=3))

st.subheader("🦋 Blueskyの投稿")
render_card_list(get_bluesky_posts("ヒグチユウコ", limit=3))


# ==================================================
# 5. 🌵 多肉植物
# ==================================================
st.header("🌵 多肉植物")

st.subheader("📝 Note (多肉植物の育て方・成長記録)")
render_card_list(get_note_posts("多肉植物", limit=3))

st.subheader("🌍 Reddit (世界の多肉植物写真)")
render_card_list(get_reddit_posts("succulents", limit=3))


# ==================================================
# 6. 🐾 猫の話題 & 海外の猫写真
# ==================================================
st.header("🐾 猫コミュニティ & 海外の猫写真")

st.subheader("🌍 Reddit (海外の猫写真・コミュニティ)")
render_card_list(get_reddit_posts("cats", limit=3))

st.subheader("🦋 Blueskyの投稿")
render_card_list(get_bluesky_posts("猫", limit=3))

st.subheader("📷 本日のランダム猫ちゃん")
st.image("https://cataas.com/cat", caption="リロードするたびに違う猫が出ます！", width=400)
