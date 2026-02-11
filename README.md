# MaxGut AI 對話系統展示專案

> 基於 Vue 3 + FastAPI 構建的即時 AI 對話系統，具備語音識別、AI 對話和即時視訊串流功能

## 📖 專案簡介

這是一個全端 AI 對話系統展示專案，整合了語音識別、AI 對話、文字轉語音(TTS)以及 WebRTC 即時串流技術，提供流暢的人機互動體驗。

### 核心功能

- 🎤 **語音輸入**：支援即時麥克風錄音與語音轉文字
- 🤖 **AI 對話**：整合 AI 對話引擎，提供智能回覆
- 🗣️ **語音合成**：使用 Edge TTS 生成自然語音
- 📹 **即時串流**：透過 WebRTC (SRS) 進行低延遲視訊串流
- 🌐 **多語言支援**：支援中文（繁體/簡體）與英文
- 💬 **對話歷史**：完整的對話記錄與管理

## 🏗️ 技術架構

### 前端技術棧
- **Vue 3** - 響應式前端框架
- **TypeScript** - 類型安全開發
- **Vite** - 快速建構工具
- **Vue Router** - 路由管理
- **Vue I18n** - 國際化支援
- **Axios** - HTTP 請求
- **Tailwind CSS** - 樣式框架
- **WebRTC (SRS SDK)** - 即時串流

### 後端技術棧
- **FastAPI** - 現代化 Python Web 框架
- **Google Cloud Speech-to-Text** - 語音識別
- **Edge TTS** - 文字轉語音
- **OpenCC** - 繁簡中文轉換
- **Uvicorn** - ASGI 伺服器

### 基礎設施
- **Docker & Docker Compose** - 容器化部署
- **Nginx** - 反向代理（可選）

## 📂 專案結構

```
maxgut_frontend_exhibition_1107_nolipsync/
├── frontend/                  # 前端專案
│   ├── src/
│   │   ├── components/       # Vue 元件
│   │   ├── composables/      # 組合式函式
│   │   ├── views/            # 頁面視圖
│   │   ├── api/              # API 請求
│   │   ├── services/         # 服務層
│   │   ├── router/           # 路由設定
│   │   ├── i18n/             # 國際化
│   │   └── utils/            # 工具函式
│   ├── public/               # 靜態資源
│   ├── Dockerfile            # 前端 Docker 設定
│   └── package.json          # 前端依賴
├── backend/                   # 後端專案
│   ├── unified_api.py        # 統一 API 服務
│   ├── requirements.txt      # Python 依賴
│   ├── Dockerfile            # 後端 Docker 設定
│   ├── replacements.json     # 文字替換規則
│   └── speech_phrases_*.txt  # 語音識別片語庫
├── docker-compose.yaml        # Docker Compose 設定
└── README.md                  # 專案說明文件
```

## 🚀 快速開始

### 前置需求

- Node.js 18+ 和 npm
- Python 3.9+
- Docker 和 Docker Compose（用於容器化部署）
- Google Cloud 服務帳戶金鑰（用於 Speech-to-Text API）

### 環境設定

#### 1. 取得 Google Cloud 憑證

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 啟用 Speech-to-Text API
3. 建立服務帳戶並下載 JSON 金鑰
4. 將金鑰檔案命名為 `wonderland-nft-5072ee803fcd.json`（或自訂名稱）
5. 放置於 `backend/` 目錄下
6. 更新 `docker-compose.yaml` 中的 `GOOGLE_APPLICATION_CREDENTIALS` 環境變數

#### 2. 設定替換規則（可選）

編輯 `backend/replacements.json` 來自訂文字替換規則，用於優化 TTS 輸出。

### 安裝與運行

#### 方式一：使用 Docker Compose（推薦）

```bash
# 1. 克隆專案
git clone <repository-url>
cd maxgut_frontend_exhibition_1107_nolipsync

# 2. 確認 Google Cloud 憑證已放置於 backend/ 目錄

# 3. 啟動服務
docker-compose up -d

# 4. 查看運行狀態
docker-compose ps

# 5. 查看日誌
docker-compose logs -f
```

服務啟動後：
- 前端：http://localhost:3006
- 後端 API：http://localhost:3566
- API 文檔：http://localhost:3566/docs

#### 方式二：本地開發

**前端**

```bash
cd frontend
npm install
npm run dev
```

**後端**

```bash
cd backend

# 建立虛擬環境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安裝依賴
pip install -r requirements.txt

# 設定環境變數
export GOOGLE_APPLICATION_CREDENTIALS="./wonderland-nft-5072ee803fcd.json"

# 啟動服務
uvicorn unified_api:app --host 0.0.0.0 --port 3566 --reload
```

## 🔧 設定說明

### Docker Compose 設定

編輯 `docker-compose.yaml` 來調整服務設定：

```yaml
services:
  frontend:
    ports:
      - "3006:3006"  # 修改前端埠號
  
  backend:
    ports:
      - "3566:3566"  # 修改後端埠號
    environment:
      - GOOGLE_APPLICATION_CREDENTIALS=/app/your-credentials.json
```

### 前端設定

修改 `frontend/src/api/chatApi.ts` 來設定 API 端點：

```typescript
const API_BASE_URL = 'http://localhost:3566';
```

## 📡 API 端點

### 語音識別
```
POST /transcribe
Content-Type: multipart/form-data
Body: file (audio file), language_code (zh-TW, en-US, etc.)
```

### AI 對話
```
POST /chat
Content-Type: application/json
Body: {
  "message": "user message",
  "conversation_id": "uuid",
  "language": "zh-TW"
}
```

### 文字轉語音
```
POST /tts
Content-Type: application/json
Body: {
  "text": "text to convert",
  "language": "zh-TW",
  "voice": "zh-TW-HsiaoChenNeural"
}
```

更多 API 詳情請查看：http://localhost:3566/docs

## 🧪 開發指令

### 前端

```bash
npm run dev      # 開發模式
npm run build    # 建構生產版本
npm run preview  # 預覽生產版本
```

### 後端

```bash
# 開發模式（自動重載）
uvicorn unified_api:app --reload

# 生產模式
uvicorn unified_api:app --host 0.0.0.0 --port 3566
```

### Docker

```bash
docker-compose up -d        # 啟動所有服務
docker-compose down         # 停止所有服務
docker-compose restart      # 重啟所有服務
docker-compose logs -f      # 查看即時日誌
docker-compose build        # 重新建構映像
```

## 🐛 疑難排解

### 問題：Google Cloud API 認證失敗
- 確認憑證檔案路徑正確
- 檢查環境變數 `GOOGLE_APPLICATION_CREDENTIALS` 是否設定
- 確認 Google Cloud 專案已啟用 Speech-to-Text API

### 問題：前端無法連接後端
- 確認後端服務已啟動
- 檢查 CORS 設定
- 驗證 API 端點 URL 是否正確

### 問題：Docker 容器無法啟動
- 檢查埠號是否被佔用
- 查看容器日誌：`docker-compose logs <service-name>`
- 確認 Docker 守護程序正在運行

### 問題：音訊錄製無法正常工作
- 確認瀏覽器已授予麥克風權限
- 使用 HTTPS 或 localhost（WebRTC 要求）
- 檢查瀏覽器控制台錯誤訊息


## 📝 授權

本專案僅供展示和學習用途。

## 👥 聯絡資訊

如有問題或建議，歡迎聯繫專案維護者。

---

**Happy Coding! 🚀**
