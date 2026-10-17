import streamlit as st
import feedparser

# アプリの基本設定
st.set_page_config(page_title="My Cinema & Life Hub", page_icon="🎬", layout="centered")
st.title("🎬 My Cinema & Life Hub")

# タブの作成
tab1, tab2, tab3, tab4 = st.tabs(["🎬 映画・上映", "✍️ コラム・SNS", "🔥 話題のニュース", "🐱 猫 & ヒグチユウコ"])

with tab1:
    st.header("映画ニュース・上映情報")
    # 映画.comのニュースを自動取得
    feed = feedparser.parse('https://eiga.com/news/feed/')
    for entry in feed.entries[:5]:
        st.write(f"**[{entry.title}]({entry.link})**")
    st.write("---")
    st.write("※後ほどここに、シネマカリテやル・シネマなど名画座の更新情報も追加できます。")

with tab2:
    st.header("映画コラム・SNS")
    st.write("エリオ・ペルティ監督のようなマニアックな作品の解説や、お気に入りの映画評論家の更新をここにまとめます。")
    # noteの映画トピックを自動取得（仮）
    st.write("📖 **ピックアップ記事**")
    feed_note = feedparser.parse('https://note.com/topic/cinema/rss')
    for entry in feed_note.entries[:5]:
        st.write(f"- [{entry.title}]({entry.link})")

with tab3:
    st.header("話題のニュース")
    # はてなブックマークのエンタメニュースを自動取得
    feed_hatebu = feedparser.parse('https://b.hatena.ne.jp/hotentry/entertainment.rss')
    for entry in feed_hatebu.entries[:5]:
        st.write(f"🔥 [{entry.title}]({entry.link})")

with tab4:
    st.header("猫 & ヒグチユウコ 最新情報")
    
    st.subheader("🍄 ヒグチユウコさん情報")
    st.write("公式サイトのNEWS: [HIGUCHI YUKO Official Website](https://higuchiyuko.tokyo/)")
    
    st.image("[https://cataas.com/cat](https://cataas.com/cat)", caption=リロードするたびに違う猫が出ます！", use_container_width=True)
    # 無料の猫画像APIを使用 
    
