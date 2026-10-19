import streamlit as st
import feedparser
import requests
import urllib.parse
import re
from datetime import datetime, timezone
import dateutil.parser

st.set_page_config(page_title="My Cinema & Life Hub", layout="wide")

st.title("🎬 My Cinema & Life Hub")

# --------------------------------------------------
# 日時パース用ヘルパー関数
# --------------------------------------------------
def parse_date(date_str):
    if not date_str:
        return datetime.min.replace(tzinfo=timezone.utc)
    try:
        dt = dateutil.parser.parse(date_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return datetime.min.replace(tzinfo=timezone.utc)


# --------------------------------------------------
# 猫画像専用取得関数（Reddit & Bluesky）
# --------------------------------------------------
def fetch_cat_photos(limit=6):
    cat_photos = []

    # 1. Reddit から画像付き投稿を取得 (r/cats, r/SupermodelCats)
    subs = ["cats", "SupermodelCats"]
    for sub in subs:
        try:
            url = f"https://www.reddit.com/r/{sub}/hot.json?limit=10"
            headers = {"User-Agent": "Mozilla/5.0"}
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code == 200:
                for child in res.json().get("data", {}).get("children", []):
                    pdata = child.get("data", {})
                    if pdata.get("stickied"):
                        continue
                    img_url = pdata.get("url", "")
                    # 画像URLの判定を拡張 (.webp や preview 等も許可)
                    if any(img_url.endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]) or "i.redd.it" in img_url:
                        cat_photos.append({
                            "title": pdata.get("title", "Reddit Cat"),
                            "link": f"https://reddit.com{pdata.get('permalink')}",
                            "image": img_url,
                            "source": f"🌍 Reddit (r/{sub})"
                        })
        except Exception:
            pass

    # 2. Bluesky から画像付き「猫」投稿を取得
    try:
        url = "https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts"
        res = requests.get(url, params={"q": "猫", "limit": 10}, timeout=5)
        if res.status_code == 200:
            for post_item in res.json().get("posts", []):
                embed = post_item.get("embed", {})
                img_url = None
                if "images" in embed and len(embed["images"]) > 0:
                    img_url = embed["images"][0].get("fullsize")
                
                if img_url:
                    record = post_item.get("record", {})
                    author = post_item.get("author", {})
                    uri_parts = post_item.get("uri", "").split("/")
                    rkey = uri_parts[-1] if uri_parts else ""
                    handle = author.get("handle", "")
                    post_url = f"https://bsky.app/profile/{handle}/post/{rkey}" if handle and rkey else "#"

                    cat_photos.append({
                        "title": record.get("text", "Bluesky 猫"),
                        "link": post_url,
                        "image": img_url,
                        "source": f"🦋 Bluesky (@{handle})"
                    })
    except Exception:
        pass

    return cat_photos[:limit]


# --------------------------------------------------
# 通常タイムライン用データ取得処理
# --------------------------------------------------
def fetch_all_items():
    items = []

    # --- 1. Bluesky ---
    bsky_queries = [
        ("名画座", "🎬 映画"),
        ("御朱印", "⛩️ 御朱印"),
        ("ヒグチユウコ", "🎨 ヒグチユウコ"),
        ("多肉植物", "🌵 多肉植物")
    ]
    for q, tag in bsky_queries:
        try:
            url = "https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts"
            res = requests.get(url, params={"q": q, "limit": 3}, timeout=5)
            if res.status_code == 200:
                for post_item in res.json().get("posts", []):
                    record = post_item.get("record", {})
                    author = post_item.get("author", {})
                    uri_parts = post_item.get("uri", "").split("/")
                    rkey = uri_parts[-1] if uri_parts else ""
                    handle = author.get("handle", "")
                    post_url = f"https://bsky.app/profile/{handle}/post/{rkey}" if handle and rkey else "#"
                    
                    embed = post_item.get("embed", {})
                    img_url = None
                    if "images" in embed and len(embed["images"]) > 0:
                        img_url = embed["images"][0].get("fullsize")

                    created_at = record.get("createdAt", "")
                    items.append({
                        "title": record.get("text", ""),
                        "link": post_url,
                        "image": img_url,
                        "source": f"🦋 Bluesky ({tag})",
                        "author": author.get("displayName") or handle,
                        "date": parse_date(created_at),
                        "date_str": created_at[:10] if created_at else ""
                    })
        except Exception:
            pass

    # --- 2. Googleニュース ---
    news_queries = [
        ("名画座 OR リバイバル上映", "🎬 映画"),
        ("特別展 OR 企画展", "🏛️ 展示"),
        ("御朱印", "⛩️ 御朱印"),
        ("ヒグチユウコ", "🎨 ヒグチユウコ")
    ]
    for q, tag in news_queries:
        try:
            encoded_query = urllib.parse.quote(q)
            rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ja&gl=JP&ceid=JP:ja"
            feed = feedparser.parse(rss_url)
            for entry in feed.entries[:3]:
                img_url = None
                if "summary" in entry:
                    match = re.search(r'src="([^"]+)"', entry.summary)
                    if match:
                        img_url = match.group(1)
                
                published = getattr(entry, "published", "")
                items.append({
                    "title": entry.title,
                    "link": entry.link,
                    "image": img_url,
                    "source": f"📰 ニュース ({tag})",
                    "author": None,
                    "date": parse_date(published),
                    "date_str": published[:16] if published else ""
                })
        except Exception:
            pass

    # --- 3. Note ---
    note_tags = [
        ("映画鑑賞", "🎬 映画"),
        ("美術展", "🏛️ 展示"),
        ("御朱印", "⛩️ 御朱印"),
        ("多肉植物", "🌵 多肉植物")
    ]
    for kw, tag in note_tags:
        try:
            encoded_kw = urllib.parse.quote(kw)
            rss_url = f"https://note.com/hashtag/{encoded_kw}/rss"
            feed = feedparser.parse(rss_url)
            for entry in feed.entries[:3]:
                img_url = None
                if hasattr(entry, 'media_thumbnail') and len(entry.media_thumbnail) > 0:
                    img_url = entry.media_thumbnail[0]['url']
                elif 'enclosures' in entry and len(entry.enclosures) > 0:
                    img_url = entry.enclosures[0]['href']

                published = getattr(entry, "published", "")
                items.append({
                    "title": entry.title,
                    "link": entry.link,
                    "image": img_url,
                    "source": f"📝 Note ({tag})",
                    "author": getattr(entry, "author", None),
                    "date": parse_date(published),
                    "date_str": published[:10] if published else ""
                })
        except Exception:
            pass

    # 投稿日時が新しい順にソート（並べ替え）
    items.sort(key=lambda x: x["date"], reverse=True)
    return items


# ==================================================
# 1. 📸 みんなのリアル猫ちゃんギャラリー (Reddit & Bluesky)
# ==================================================
st.header("🐾 街と世界の猫ちゃんギャラリー")
cat_photos = fetch_cat_photos(limit=6)

if cat_photos:
    cols = st.columns(3)  # 3列に並べて表示
    for idx, photo in enumerate(cat_photos):
        with cols[idx % 3]:
            st.image(photo["image"], use_container_width=True)
            st.caption(f"**{photo['source']}**")
            st.markdown(f'<a href="{photo["link"]}" target="_blank" rel="noopener noreferrer">{photo["title"][:40]}...</a>', unsafe_allow_html=True)
            st.write("---")
else:
    st.caption("※猫画像の読み込み中、または投稿が見つかりませんでした。")

st.write("---")


# ==================================================
# 2. 📰 最新タイムライン (映画・展示・御朱印・多肉・ヒグチユウコ)
# ==================================================
st.header("📰 最新タイムライン")
all_items = fetch_all_items()

if not all_items:
    st.info("データの取得に失敗したか、現在表示できる投稿がありません。")
else:
    for item in all_items:
        col1, col2 = st.columns([1, 3])
        with col1:
            if item.get("image"):
                st.image(item["image"], use_container_width=True)
            else:
                st.markdown("🖼️ *(画像なし)*")
        with col2:
            st.caption(f"**{item['source']}** {('・ ' + item['date_str']) if item['date_str'] else ''}")
            st.markdown(f'<a href="{item["link"]}" target="_blank" rel="noopener noreferrer">**{item["title"]}**</a>', unsafe_allow_html=True)
            if item.get("author"):
                st.caption(f"by {item['author']}")
        st.write("---")

# 一番下のランダム猫ちゃん
st.subheader("📷 本日のランダム猫ちゃん")
st.image("https://cataas.com/cat", caption="リロードするたびに違う猫が出ます！", width=300)
