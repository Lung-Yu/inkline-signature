# Inkline 藝術簽名產生器

輸入中英文姓名，自動設計藝術簽名，一筆一劃示範筆順，並可播放全螢幕品牌動畫。
純靜態網站，沒有後端、沒有建置步驟，任何靜態主機都能部署。

## 目錄

```
site/                 ← 部署這個資料夾
  index.html          網頁本體（HTML + CSS + JS 單一檔案）
  config.js           預設名字設定（見下方「預設名字」）
  hands.json          英文 12 款簽名筆跡資料（約 1.1 MB，gzip 後約 0.36 MB）
  hz/h0–h96.json      中文筆順與楷書輪廓，依字分 97 片；只下載名字用到的分片
  _headers            Netlify / Cloudflare Pages 的快取設定
nginx.conf, Dockerfile, docker-compose.yml, config.js.template  自架用
tools/                重新產生資料的腳本（部署不需要）
licenses/             第三方授權，部署時請一併保留
```

## 本機預覽

資料用 `fetch()` 載入，直接雙擊 `index.html`（file://）會讀不到資料，請開一個本機伺服器：

```bash
cd site && python3 -m http.server 8080
# 打開 http://localhost:8080
```

## 部署

| 平台 | 做法 |
|---|---|
| Netlify | 把 `site/` 拖進 app.netlify.com/drop，或連 Git 時 Publish directory 設 `site` |
| Cloudflare Pages | Build command 留空，Build output directory 設 `site` |
| Vercel | Root Directory 設 `site`，Framework 選 Other，不需 build |
| GitHub Pages | 把 `site/` 的內容推到 `gh-pages` 分支，或在 Actions 上傳 `site` 為 artifact |
| Nginx / Docker | `docker build -t inkline . && docker run -p 8080:80 inkline` |
| S3 / GCS / OSS | 上傳 `site/` 內容，`index.html` 設為首頁；`.json` 的 Content-Type 設為 `application/json` |

可以放在子路徑（例如 `https://example.com/signature/`），所有資料都用相對路徑載入。

## 預設名字

打開頁面時姓名欄的預設值。沒設定就用 `index.html` 內建的值。

- Docker：用環境變數設定，容器啟動時會重新產生 `config.js`
  ```bash
  docker run -p 8080:80 -e DEFAULT_NAME_LATIN="Amy Chen" -e DEFAULT_NAME_CN=林雨晴 inkline
  ```
  用 docker compose 的話，寫在同目錄的 `.env`，或直接帶在指令前面：
  ```bash
  DEFAULT_NAME_LATIN="Amy Chen" DEFAULT_NAME_CN=林雨晴 docker compose up -d --build
  ```
  名字裡不能有 `"` 或 `\`。
- 其他靜態主機（沒有執行環境，讀不到環境變數）：直接改 `site/config.js`。

## 外部相依

只有 Google Fonts（Bodoni Moda、IBM Plex Mono、Noto Sans TC、Noto Serif TC）。
在無法連到 Google 的環境（例如中國大陸）字型會退回系統字型，功能不受影響。
若要完全離線，把字型下載到 `site/fonts/`，改寫 `index.html` 開頭的 `<link>` 為本地 `@font-face`。

## 瀏覽器支援

近兩年的 Chrome、Edge、Safari、Firefox（需要 Canvas `Path2D`、`fetch`、`ResizeObserver`）。
全螢幕按鈕在 iPhone Safari 上只能放大到整個分頁，這是 iOS 的限制。

## 重新產生資料（選用）

```bash
# 英文筆跡：下載字型 → 萃取骨架
pip install pillow numpy scipy scikit-image fonttools
bash tools/fetch_fonts.sh                     # 產生 fonts/*.ttf
cd fonts && OUT=../site/hands.json python3 -I ../tools/extract_font_skeletons.py *.ttf

# 中文筆順
npm pack hanzi-writer-data && mkdir src && tar xzf hanzi-writer-data-*.tgz -C src
python3 -I tools/build_hanzi_shards.py src/package site/hz
```

`tools/symbols.reference.js` 是名字內符號（♡ ★ ♪ :) <3 …）的手繪筆跡與解析程式，已內嵌在 `index.html`，此檔僅供閱讀與修改參考。

## 授權

程式碼由你自行決定授權。英文筆跡資料衍生自 SIL OFL 1.1 字型，中文資料衍生自 Arphic Public License 資料，
兩者都允許商業使用，但衍生資料須沿用原授權並保留聲明，細節見 `licenses/NOTICE.md`。
