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

    # --- 1. Bluesky (名画座・単館映画館のキーワードを追加) ---
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
                        "source": f"🦋 Bluesky ({
