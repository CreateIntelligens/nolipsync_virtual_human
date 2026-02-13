# MaxGut AI 對話系統展示專案 (展場優化版)

> 基於 Vue 3 + FastAPI 構建的即時 AI 對話系統，針對展場高並發與噪音環境進行深度優化。

## 📖 專案簡介

這是一個專為展覽現場設計的全端 AI 對話系統。整合了語音識別、AI 對話、文字轉語音(TTS)技術，並透過 Nginx 整合入口，提供穩定且流暢的人機互動體驗。

### 核心功能與優化

- 🎤 **抗噪語音輸入**：
    - **VAD (語音活動偵測)**：針對吵雜環境優化，具備首聲偵測機制，防止背景音誤觸。
    - **空內容攔截**：後端自動過濾無效錄音，避免 AI 產生誤導回覆。
    - **全雙工支援**：支援在虛擬人說話時直接插話錄音。
- 🤖 **高效 AI 對話**：
    - **全異步 (Async) 架構**：後端使用 `httpx` 非阻塞請求，支援多台設備同時對話。
    - **多進程部署**：預設開啟 8 個 Workers，輕鬆應對 20+ 台 iPad 並發需求。
- 🗣️ **語音合成**：整合 Edge TTS 生成自然語音，支援中英文切換。
- 📹 **虛擬人動態視覺**：
    - **智能影片切換**：根據閒置、說話狀態自動切換本地 MP4 影片，效能穩定。
    - **即時響應**：聲音播放結束立即恢復閒置動畫，無感切換。
- 🌐 **多環境支援**：自動判斷 IP 或 Domain 環境，解決 HTTPS 混合內容與防火牆端口限制。

## 🏗️ 技術架構

### 前端技術棧
- **Vue 3** - 響應式前端框架
- **TypeScript** - 類型安全開發
- **Vite** - 快速建構工具
- **Tailwind CSS** - 樣式框架
- **Web Audio API** - 高性能音訊處理與 VAD 實作

### 後端技術棧
- **FastAPI** - 現代化 Python 異步 Web 框架
- **Httpx** - 異步 HTTP 請求庫 (用於 AI Chat 代理)
- **Google Cloud STT** - 專業級語音識別
- **Edge TTS** - 文字轉語音
- **Nginx** - 整合式反向代理與靜態資源託管

## 📂 專案結構

```
maxgut_frontend_exhibition_1107_nolipsync/
├── frontend/                  # 前端專案 (Vue 3)
│   ├── Dockerfile            # 整合 Nginx 轉發邏輯
│   └── src/
│       ├── api/chatApi.ts    # 環境自動判斷與 API 封裝
│       └── composables/
│           ├── useAudioRecording.ts # 加強型 VAD 邏輯
│           └── useChat.ts           # 對話狀態管理
├── backend/                   # 後端專案 (FastAPI)
│   ├── unified_api.py        # 全異步 API 實作
│   ├── requirements.txt      # 包含 httpx 等異步依賴
│   └── Dockerfile            # 配置 --workers 多進程啟動
├── docker-compose.yaml        # 簡化後的容器編排
└── README.md                  # 專案說明文件
```

## 🚀 快速開始

### 前置需求
- Docker 與 Docker Compose
- Google Cloud 服務帳戶金鑰 (`.json`)，放置於 `backend/` 目錄。

### 安裝與運行 (展場部署)

```bash
# 1. 確保憑證到位
# 預設金鑰名稱：wonderland-nft-5072ee803fcd.json

# 2. 建構並啟動
docker-compose build
docker-compose up -d
```

服務啟動後入口：
- **主要入口 (Nginx)**: `http://localhost:3006` (或您的 Domain)
- **後端 API 直接存取**: `http://localhost:3566`

## 🔧 展場優化設定

### VAD 靈敏度調整
若在極度吵雜環境下仍有誤觸，可修改 `frontend/src/composables/useAudioRecording.ts`：
- `SILENCE_THRESHOLD`: 提高此值 (如 0.15) 以過濾更強的背景音。
- `SPEECH_ACTIVATION_THRESHOLD`: 提高啟動門檻。

### 並發效能調整
若 iPad 數量超過 20 台且反應變慢，可修改 `backend/Dockerfile` 中的 `--workers` 參數：
- 建議值：`(CPU 核心數 * 2) + 1`

## 📡 API 端點

### 語音轉文字 + AI 對話 (異步)
```
POST /transcribe4
```
- 後端會先透過 Google STT 轉文字。
- 若文字為空，回傳 `status: "empty"`。
- 若文字有效，異步呼叫 AI 並回傳結果。

### 文字轉語音 (Edge TTS)
```
POST /tts
```
- 直接串接 Microsoft 免費 TTS 接口，支援 `wav` 與 `mp3`。

## 🐛 疑難排解

### HTTPS Domain 無法存取 API
本專案已實作「統一入口」機制。請確保透過 **Port 3006** 進入。
- 正確路徑：`https://your-domain.ai:3006`
- Nginx 會自動將 `/api` 請求轉發給 3566 端口，避免 HTTPS 混合內容錯誤。

---

**MaxGut AI Exhibition Team** 🚀
