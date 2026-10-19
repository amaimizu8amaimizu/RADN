# --------------------------------------------------
# 1. 猫ギャラリー用 Bluesky 取得（本物の猫ちゃんフィルター版）
# --------------------------------------------------
def fetch_bluesky_cat_photos(limit=6):
    cat_photos = []
    # #猫のいる暮らし や #保護猫 などのハッシュタグで本物の猫ちゃんをピンポイント検索
    posts = fetch_bluesky_raw("#猫のいる暮らし OR #猫 OR #愛猫", limit=30)
    
    # 除外したいアニメ・マンガ関連の単語リスト
    ng_words = ["ハイキュー", "音駒", "コスプレ", "イラスト", "二次創作", "VTuber", "アクスタ", "フィギュア"]

    for post_item in posts:
        record = post_item.get("record", {})
        text = record.get("text", "")

        # NGワードが含まれている場合はスキップ（除外）
        if any(ng in text for ng in ng_words):
            continue

        embed = post_item.get("embed", {})
        img_url = None
        
        if "images" in embed and len(embed["images"]) > 0:
            img_url = embed["images"][0].get("fullsize") or embed["images"][0].get("thumb")
        elif embed.get("$type") == "app.bsky.embed.recordWithMedia#view":
            media = embed.get("media", {})
            if "images" in media and len(media["images"]) > 0:
                img_url = media["images"][0].get("fullsize") or media["images"][0].get("thumb")

        if img_url:
            author = post_item.get("author", {})
            uri_parts = post_item.get("uri", "").split("/")
            rkey = uri_parts[-1] if uri_parts else ""
            handle = author.get("handle", "")
            post_url = f"https://bsky.app/profile/{handle}/post/{rkey}" if handle and rkey else "#"

            display_text = text[:35] + "..." if len(text) > 35 else (text or "愛猫の写真")

            cat_photos.append({
                "title": display_text,
                "link": post_url,
                "image": img_url,
                "source": f"🦋 Bluesky (@{handle})"
            })
            if len(cat_photos) >= limit:
                break
    return cat_photos
