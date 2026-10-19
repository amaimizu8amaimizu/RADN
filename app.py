import streamlit as st
import feedparser
import requests
import urllib.parse
import re
from datetime import datetime, timezone
import dateutil.parser

st.set_page_config(page_title="My Cinema & Life Hub", layout="wide")

# ==================================================
# 🎬 映画館スケジュール（サイドバーメニュー）
# ==================================================
st.sidebar.header("🎬 映画館スケジュール")

theaters = [
    ("アップリンク吉祥寺", "https://joji.uplink.co.jp/"),
    ("早稲田松竹", "http://wasedashotiku.com/"),
    ("新文芸坐", "https://www.shin-bungeiza.com/"),
    ("キネカ大森", "https://ttcg.jp/kineka_oomori/"),
    ("シネマート新宿", "https://www.cinemart.co.jp/theater/shinjuku/"),
    ("ケイズシネマ", "https://www.ks-cinema.com/"),
    ("新宿シネマカリテ", "https://qualite.musashino-k.jp/"),
    ("新宿武蔵野館", "https://musashino-k.jp/"),
    ("目黒シネマ", "http://www.megurocinema.net/"),
    ("下高井戸シネマ", "http://www.shimotakaido-cinema.com/"),
    ("Stranger", "https://stranger.jp/"),
    ("テアトルシネマグループ", "https://ttcg.jp/"),
    ("ヒューマントラストシネマ渋谷", "https://ttcg.jp/human_shibuya/"),
    ("HUMAX CINEMA", "https://www.humax-cinema.co.jp/"),
    ("イメージフォーラム", "http://www.imageforum.co.jp/theatre/"),
    ("CINE QUINTO／シネクイント", "https://www.cinequinto.com/"),
    ("ユーロスペース", "http://www.eurospace.co.jp/"),
    ("シネマヴェーラ", "http://www.cinemavera.com/"),
    ("ヒューマントラストシネマ有楽町", "https://ttcg.jp/human_yurakucho/"),
    ("立川の映画館 シネマ・ワン＆シネマ・ツー｜シネマシティ", "https://cinemacity.co.jp/")
]

for name, url in theaters:
    st.sidebar.markdown(f'• <a href="{url}" target="_blank" rel="noopener noreferrer">{name}</a>', unsafe_allow_html=True)


# ==================================================
# メイン画面ヘッダー
# ==================================================
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
# Bluesky 日本の猫画像投稿 取得関数
# --------------------------------------------------
def fetch_bluesky_cat_photos(limit=6):
    cat_photos = []
    try:
        url = "https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts"
        # 「猫」や「ねこ」で最新画像付き投稿を検索
        res = requests.get(url, params={"q": "猫", "limit": 25}, timeout=5)
        if res.status_code == 200:
            for post_item in res.json().get("posts", []):
                embed = post_item.get("embed", {})
                img_url = None
                
                # 画像の抽出処理
                if "images" in embed and len(embed["images"]) > 0:
                    img_url = embed["images"][0].get("fullsize") or embed["images"][0].get("thumb")
                elif embed.get("$type") == "app.bsky.embed.recordWithMedia#view":
                    media = embed.get("media", {})
                    if "images" in media and len(media["images"]) > 0:
                        img_url = media["images"][0].get("fullsize") or media["images"][0].get("thumb")

                if img_url:
                    record = post_item.get("record", {})
                    author = post_item.get("author", {})
                    uri_parts = post_item.get("uri", "").split("/")
                    rkey = uri_parts[-1] if uri_parts else ""
                    handle = author.get("handle", "")
                    post_url = f"https://bsky.app/profile/{handle}/post/{rkey}" if handle and rkey else "#"

                    text = record.get("text", "")
                    display_text = text[:35] + "..." if len(text) > 35 else (text or "愛猫の写真")

                    cat_photos.append({
                        "title": display_text,
                        "link": post_url,
                        "image": img_url,
                        "author": author.get("displayName") or handle,
                        "source": f"🦋 Bluesky (@{handle})"
                    })
                    if len(cat_photos) >= limit:
                        break
    except Exception:
        pass

    return cat_photos


# --------------------------------------------------
# 通常タイムライン用データ取得処理
# --------------------------------------------------
def fetch_all_items():
    items = []

    # --- 1. Bluesky ---
    bsky_queries = [
        ("名画座", "🎬 名画座"),
        ("早稲田松竹", "🎬 映画館"),
        ("新文芸坐", "🎬 映画館"),
        ("シネマカリテ", "🎬 映画館"),
        ("武蔵野館", "🎬 映画館"),
        ("目黒シネマ", "🎬 映画館"),
        ("アップリンク吉祥寺", "🎬 映画館"),
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

    items.sort(key=lambda x: x["date"], reverse=True)
    return items


# ==================================================
# 1. 🐾 街とSNSのリアル猫ちゃんギャラリー (Bluesky)
# ==================================================
st.header("🐾 Blueskyのリアル猫ちゃんギャラリー")
cat_photos = fetch_bluesky_cat_photos(limit=6)

if cat_photos:
    cols = st.columns(3)
    for idx, photo in enumerate(cat_photos):
        with cols[idx % 3]:
            st.image(photo["image"], use_container_width=True)
            st.caption(f"**{photo['source']}**")
            st.markdown(f'<a href="{photo["link"]}" target="_blank" rel="noopener noreferrer">{photo["title"]}</a>', unsafe_allow_html=True)
            st.write("---")
else:
    st.caption("※Blueskyから猫画像の投稿を読み込み中...")

st.write("---")


# ==================================================
# 2. 📰 最新タイムライン
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
