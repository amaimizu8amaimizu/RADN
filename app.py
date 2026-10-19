
import streamlit as st
import feedparser

st.title("🎬 My Cinema & Life Hub")

# 1. 映画ニュース・上映情報
st.header("映画ニュース・上映情報")
# 映画.comのニュースを自動取得
feed = feedparser.parse('https://eiga.com/news/feed/')
for entry in feed.entries[:5]:
    st.markdown(f'• <a href="{entry.link}" target="_blank" rel="noopener noreferrer">**{entry.title}**</a>', unsafe_allow_html=True)
    st.write("---")

st.write("※後ほどここに、シネマカリテやル・シネマなど名小座の更新情報も追加できます。")
st.write("---")

# 2. 映画コラム・SNS
st.header("映画コラム・SNS")
st.write("エリオ・ペルティ監督のようなマニアックな作品の解説や、お気に入りの映画評論家の更新をここにまとめます。")
# noteの映画トピックを取得（仮）
st.write("🍿 **ピックアップ記事**")
feed_note = feedparser.parse('https://note.com/topic/cinema/rss')
for entry in feed_note.entries[:5]:
    st.markdown(f'• <a href="{entry.link}" target="_blank" rel="noopener noreferrer">{entry.title}</a>', unsafe_allow_html=True)
    st.write("---")

# 3. 話題のニュース
st.header("話題のニュース")
# はてなブックマークのエンタメニュースを自動取得
feed_hatebu = feedparser.parse('https://b.hatena.ne.jp/hotentry/entertainment.rss')
for entry in feed_hatebu.entries[:5]:
    st.markdown(f'• <a href="{entry.link}" target="_blank" rel="noopener noreferrer">{entry.title}</a>', unsafe_allow_html=True)
    st.write("---")

# 4. ヒグチユウコ 最新情報
st.header("ヒグチユウコ 最新情報")
st.markdown('• <a href="https://higuchiyuko.tokyo/" target="_blank" rel="noopener noreferrer">公式サイトのNEWS: HIGUCHI YUKO Official Website</a>', unsafe_allow_html=True)
st.write("---")

# 5. 本日の猫ちゃん
st.header("🐾 本日の猫ちゃん")
st.image("https://cataas.com/cat", caption="リロードするたびに違う猫が出ます！", use_container_width=True)
