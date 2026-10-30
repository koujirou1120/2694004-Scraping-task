import csv
from urllib.parse import urljoin, urlparse
import time
from bs4 import BeautifulSoup
import requests

# 1. クロール対象のベースURL（武蔵野大学）
base_url = "https://www.musashino-u.ac.jp/"
parsed_base = urlparse(base_url)

# 訪問済みURLと、結果を格納する辞書
visited_urls = set()
sitemap_dict = {}

# 探索するURLのキュー（幅優先探索用）
queue = [base_url]

print("スクレイピングを開始します...")

while queue:
  current_url = queue.pop(0)

  if current_url in visited_urls:
    continue

  # 同一ドメインチェック
  parsed_current = urlparse(current_url)
  if parsed_current.netloc != parsed_base.netloc:
    continue

  visited_urls.add(current_url)
  print(f"取得中: {current_url}")

  try:
    # サーバーへの負荷軽減（必ず入れる）
    time.sleep(1.0)

    response = requests.get(current_url, timeout=10)
    # 文字コードの自動判定・設定
    response.encoding = response.apparent_encoding

    if response.status_code != 200:
      continue

    soup = BeautifulSoup(response.text, "html.parser")

    # <title>タグの取得
    title_tag = soup.find("title")
    title_text = title_tag.get_text().strip() if title_tag else "No Title"

    # 辞書に格納 (key: URL, value: <title>文字列)
    sitemap_dict[current_url] = title_text

    # ページ内のリンクをすべて取得してキューに追加
    for a_tag in soup.find_all("a", href=True):
      href = a_tag["href"]
      # 絶対URLに変換
      absolute_url = urljoin(current_url, href)

      # フラグメント(#)などを除去して正規化
      parsed_abs = urlparse(absolute_url)
      clean_url = f"{parsed_abs.scheme}://{parsed_abs.netloc}{parsed_abs.path}"

      if clean_url not in visited_urls and parsed_abs.netloc == parsed_base.netloc:
        if clean_url not in queue:
          queue.append(clean_url)

  except Exception as e:
    print(f"エラー発生 ({current_url}): {e}")

# 2. 辞書型変数をCSVファイルに保存
csv_filename = "musashino_u_sitemap.csv"
with open(csv_filename, mode="w", encoding="utf-8-sig", newline="") as f:
  writer = csv.writer(f)
  # ヘッダー
  writer.writerow(["URL", "Title"])
  # データ書き込み
  for url, title in sitemap_dict.items():
    writer.writerow([url, title])

print(f"完了しました！合計 {len(sitemap_dict)} 件のページを保存しました。")