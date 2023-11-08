import os
import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
from datetime import datetime, timedelta

# 環境変数の設定
youtube_api_key = st.secrets.youtube_api.key

# YouTube Data APIのキーをセット
youtube = build('youtube', 'v3', developerKey=youtube_api_key)

# Streamlitアプリの設定
st.title('動画分析ツール')

# 検索条件のUI
expander = st.expander('良質な動画とは何でしょうか？')
expander.write('登録者数＜再生回数は良質な動画')
search_query = st.text_input('キーワードを入力してください:')
days = st.slider('投稿された過去日付を何日まで遡るか指定してください（過去30日まで）:', 1, 30, 2)
expander = st.expander('投稿日の設定推奨は2日です')
expander.write('情報鮮度の観点からも投稿日から2日で再生回数は頭打ち それ以降は緩やかに伸びるかそのままの数値を維持する傾向が強い')
max_results = st.slider('取得する動画の数を選択してください（最大30件まで）:', 1, 30, 10)

"""
検索結果を基にサムネイルの分析をしていきましょう！\n
再生回数が多い動画のサムネイルはクリックしたくなるように加工されています。\n
★フォントは？画像の配色は？文字サイズは？サムネイルの文言は？★\n
"""

response = None  # response変数を初期化

if st.button('検索結果を表示します'):
    # 日数を計算してRFC 3339フォーマットに変換
    published_after = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%dT00:00:00Z')

    # YouTube Data APIを使用して動画を検索
    request = youtube.search().list(
        q=search_query,
        type='video',
        order='viewCount',
        videoDefinition='high',
        videoEmbeddable='true',
        publishedAfter=published_after,
        maxResults=max_results,
        part='snippet'
    )
    response = request.execute()

# responseがNoneでないことを確認してから処理を続行
if response is not None:
    # 検索結果をPandas DataFrameに保存
    videos = []
    view_counts = []

    for video in response['items']:
        video_id = video['id']['videoId']
        title = video['snippet']['title']
        thumbnail_url = video['snippet']['thumbnails']['high']['url']
        video_url = f'https://www.youtube.com/watch?v={video_id}'
        videos.append({'Title': title, 'Video URL': video_url, 'Thumbnail URL': thumbnail_url})

        # ビデオの詳細情報を取得（再生回数を含む）
        video_response = youtube.videos().list(
            part="statistics",
            id=video_id
        ).execute()

        # 再生回数を取得してリストに追加
        view_count = video_response["items"][0]["statistics"]["viewCount"]
        view_counts.append(view_count)

    # DataFrameを作成して結果を表示
    df = pd.DataFrame(videos)
    df['再生回数'] = view_counts

    # サムネイルを画像として表示
    for index, row in df.iterrows():
        st.image(row['Thumbnail URL'], caption=row['Title'], width=320)
        st.write(f'Title: {row["Title"]}')
        st.write(f'Video URL: {row["Video URL"]}')
        st.write(f'再生回数: {row["再生回数"]}')  # 再生回数を表示
        st.write("----------")
