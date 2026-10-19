import streamlit as st
import feedparser
import requests
import urllib.parse
import re
from datetime import datetime, timezone
import dateutil.parser

st.set_page_config(page_title="RADNの箱", layout="wide")

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
st.title("📦 RADNの箱")

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
# Bluesky 認証（ログイン）処理
# --------------------------------------------------
@st.cache_data(ttl=300)
def get_bsky_token():
    try:
        handle = st.secrets.get("BSKY_HANDLE", "")
        password = st.secrets.get("BSKY_PASSWORD", "")
        if not handle or not password:
            return None
        
        url = "https://bsky.social/xrpc/com.atproto.server.createSession"
        res = requests.post(url, json={"identifier": handle, "password": password}, timeout=5)
        if res.status_code == 200:
            return res.json().get("accessJwt")
    except Exception:
        pass
    return None

# --------------------------------------------------
# Bluesky 通信・取得処理（認証付き）
# --------------------------------------------------
def fetch_bluesky_raw(query, limit=5):
    token = get_bsky_token()
    url = "https://bsky.social/xrpc/app.bsky.feed.searchPosts"
    headers = {"User-Agent": "Mozilla/5.0"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    params = {"q": query, "limit": limit}
    try:
        res = requests.get(url, headers=headers, params=params, timeout=5)
        if res.status_code == 200:
            return res.json().get("posts", [])
    except Exception:
        pass
    return []


# --------------------------------------------------
# 1. 猫ギャラリー用 Bluesky 取得（リアル猫フィルター付き）
# --------------------------------------------------
def fetch_bluesky_cat_photos(limit=6):
    cat_photos = []
    posts = fetch_bluesky_raw("#猫のいる暮らし OR #猫 OR #愛猫", limit=30)
    ng_words = ["ハイキュー", "音駒", "コスプレ", "イラスト", "二次創作", "VTuber", "アクスタ", "フィギュア"]

    for post_item in posts:
        record = post_item.get("record", {})
        text = record.get("text", "")

        if any(ng in text for ng in ng_words):
            continue

        embed = post_item.get("embed", {})
        img_url = None
        
        if "images" in embed and len(embed["images"]) > 0:
            img_url = embed["images"][0].
