# 使用 Python 3.10 作為基礎映像
FROM python:3.10-slim

# 設定工作目錄
WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 複製 requirements.txt 並安裝 Python 依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式檔案
COPY . .

# 暴露端口
EXPOSE 3566

# 啟動命令
# 使用 --workers 增加並發處理能力，建議值為 (2 x CPU核心數) + 1
CMD ["uvicorn", "unified_api:app", "--host", "0.0.0.0", "--port", "3566", "--workers", "8"]
