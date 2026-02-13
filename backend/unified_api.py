"""
Unified API Service for MaxGut Frontend Exhibition
整合語音識別、AI對話、文字轉語音功能
Port: 3566
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import Response, JSONResponse ,StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.cloud import speech
from datetime import datetime
import edge_tts
import opencc
import httpx
import json
import os
import re
from io import BytesIO
from typing import List
import asyncio

# 初始化
app = FastAPI(title="MaxGut Unified API Service")

# 全域 AsyncClient
async_client = httpx.AsyncClient(timeout=30.0, verify=False)

@app.on_event("shutdown")
async def shutdown_event():
    await async_client.aclose()

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenCC 繁簡轉換
converter = opencc.OpenCC('s2t')

# Google Cloud 憑證設定
GOOGLE_CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), "wonderland-nft-5072ee803fcd.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_CREDENTIALS_PATH

# 載入文字替換規則
REPLACE_RULES = []
try:
    replacements_path = os.path.join(os.path.dirname(__file__), 'replacements.json')
    with open(replacements_path, 'r', encoding='utf-8') as f:
        REPLACE_RULES = json.load(f)
    print(f'[{datetime.now()}] Loaded {len(REPLACE_RULES)} replacement rules')
except Exception as e:
    print(f'[{datetime.now()}] Warning: Could not load replacements.json: {str(e)}')


def load_speech_phrases(file_path: str) -> List[str]:
    """載入語音識別關鍵詞"""
    try:
        phrases = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                phrase = line.strip()
                if phrase:
                    phrases.append(phrase)
        print(f"[{datetime.now()}] Loaded {len(phrases)} speech phrases from {file_path}")
        return phrases
    except Exception as e:
        print(f"[{datetime.now()}] Warning: Could not load {file_path}: {str(e)}")
        return []


def apply_text_replacements(text: str) -> str:
    """應用文字替換規則"""
    if not REPLACE_RULES:
        return text
    
    original_text = text
    for rule in REPLACE_RULES:
        flag_val = 0
        for f in rule.get('flags', []):
            flag_val |= getattr(re, f, 0)
        text = re.sub(rule['pattern'], rule['replacement'], text, flags=flag_val)
    
    if text != original_text:
        print(f'[{datetime.now()}] Text after replacements: {text}')
    
    return text


def apply_text_corrections(text: str) -> str:
    """應用文字修正（縮寫、格式等）"""
    corrections = [
        (r'(?<![A-Za-z])O\W*E\W*M(?![A-Za-z])', 'OEM'),
        (r'(?<![A-Za-z])O\W*D\W*M(?![A-Za-z])', 'ODM'),
        (r'(?<![A-Za-z])M\W*O\W*Q(?![A-Za-z])', 'MOQ'),
        (r'(?<![A-Za-z])G\W*M\W*P(?![A-Za-z])', 'GMP'),
        (r'(?<![A-Za-z])I\W*S\W*O(?![A-Za-z])', 'ISO'),
        (r'(?<![A-Za-z])H\W*A\W*L\W*A(?![A-Za-z])', 'Halal'),
        (r'(?<![A-Za-z])S\W*P\W*F(?![A-Za-z])', 'SPF'),
        (r'(?<![A-Za-z])C\W*O\W*A(?![A-Za-z])', 'COA'),
        (r'(?<![A-Za-z])E\W*G\W*F(?![A-Za-z])', 'EGF'),
        (r'產品品質', '產品的品質'),
    ]
    
    for pattern, replacement in corrections:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    # 移除末尾句號
    text = re.sub(r'。$', '', text)
    
    return text


# ==================== API Models ====================

class TTSRequest(BaseModel):
    text: str
    voice: str = "zh-TW-HsiaoChenNeural"
    rate: str = "+0%"  # 語速調整 -50% 到 +100%
    volume: str = "+0%"  # 音量調整 -50% 到 +100%
    pitch: str = "+0Hz"  # 音調調整
    format: str = "mp3"  # 音檔格式: mp3 或 wav

class VoiceInfo(BaseModel):
    name: str
    short_name: str
    gender: str
    locale: str


class TextChatRequest(BaseModel):
    text: str
    conversation_id: str


# ==================== API Endpoints ====================

@app.get("/")
async def root():
    return {
        "service": "MaxGut Unified API",
        "version": "1.0",
        "port": 3566,
        "endpoints": {
            "/transcribe4": "POST - 中文語音轉文字 + AI對話",
            "/transcribe4_en": "POST - 英文語音轉文字 + AI對話",
            "/ai_chat4": "POST - 中文純文字對話",
            "/ai_chat4_en": "POST - 英文純文字對話",
            "/tts": "POST - 文字轉語音"
        }
    }


@app.post("/transcribe4")
async def transcribe_zh(
    audio: UploadFile = File(...),
    conversation_id: str = Form("default_conversation_id")
):
    """中文語音轉文字 + AI 對話"""
    try:
        print(f"[{datetime.now()}] 開始中文語音轉錄...")
        
        # 初始化 Google Speech client
        client = speech.SpeechClient()
        audio_content = await audio.read()
        
        # 載入中文關鍵詞
        speech_phrases = load_speech_phrases(
            os.path.join(os.path.dirname(__file__), "speech_phrases_maxgut_zh.txt")
        )
        
        speech_contexts = []
        if speech_phrases:
            speech_contexts = [
                speech.SpeechContext(phrases=speech_phrases, boost=20.0)
            ]
        
        # Google Speech API 配置
        audio_obj = speech.RecognitionAudio(content=audio_content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="zh-TW",
            enable_automatic_punctuation=True,
            speech_contexts=speech_contexts
        )
        
        # 執行識別
        response = client.recognize(config=config, audio=audio_obj)
        
        # 提取識別結果
        input_text = ""
        for result in response.results:
            input_text += result.alternatives[0].transcript
        
        # 應用文字修正
        input_text = apply_text_corrections(input_text).strip()
        
        # 【關鍵優化】如果識別出的文字太短或為空，不觸發 AI，直接返回
        if not input_text or len(input_text) < 1:
            print(f"[{datetime.now()}] 識別結果為空，不觸發 AI。")
            return JSONResponse({
                "input_text": "",
                "text": "",
                "conversation_id": conversation_id,
                "status": "empty"
            })

        print(f"[{datetime.now()}] 轉錄完成: {input_text}")
        
        # 呼叫 AI 聊天 API
        ai_url = "https://cs01-line.ai360.workers.dev/api/chat"
        ai_payload = {
            "text": converter.convert(input_text),
            "conversation_id": conversation_id,
            "notebook_id": "notebook:47rayc7fhfiower8b918"
        }
        
        print(f"[{datetime.now()}] 呼叫 AI 聊天機器人...")
        try:
            ai_response = await async_client.post(ai_url, json=ai_payload)
            if ai_response.status_code != 200:
                print(f"[{datetime.now()}] AI 伺服器回傳錯誤代碼: {ai_response.status_code}")
                message = "抱歉，系統目前忙碌中，請稍後再試。"
            else:
                ai_response_json = ai_response.json()
                ai_messages = [msg for msg in ai_response_json['messages'] if msg['type'] == 'ai']
                message = ai_messages[-1]['content'] if ai_messages else "抱歉，我無法理解您的問題。"
        except Exception as ai_err:
            print(f"[{datetime.now()}] 呼叫 AI 失敗: {str(ai_err)}")
            message = "抱歉，我現在有點不舒服，請再對我說一次。"
        
        # 應用文字修正和替換
        message = apply_text_corrections(message)
        message = re.sub(r'\*+', '', message)  # 移除星號
        
        return JSONResponse({
            "input_text": converter.convert(input_text),
            "text": converter.convert(message),
            "conversation_id": conversation_id,
            "status": "success"
        })
        
    except Exception as e:
        print(f"[{datetime.now()}] 轉錄錯誤: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/transcribe4_en")
async def transcribe_en(
    audio: UploadFile = File(...),
    conversation_id: str = Form("default_conversation_id")
):
    """英文語音轉文字 + AI 對話"""
    try:
        print(f"[{datetime.now()}] 開始英文語音轉錄...")
        
        # 初始化 Google Speech client
        client = speech.SpeechClient()
        audio_content = await audio.read()
        
        # 載入英文關鍵詞
        speech_phrases = load_speech_phrases(
            os.path.join(os.path.dirname(__file__), "speech_phrases_maxgut_en.txt")
        )
        
        speech_contexts = []
        if speech_phrases:
            speech_contexts = [
                speech.SpeechContext(phrases=speech_phrases, boost=20.0)
            ]
        
        # Google Speech API 配置
        audio_obj = speech.RecognitionAudio(content=audio_content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="en-US",
            enable_automatic_punctuation=True,
            speech_contexts=speech_contexts
        )
        
        # 執行識別
        response = client.recognize(config=config, audio=audio_obj)
        
        # 提取識別結果
        input_text = ""
        for result in response.results:
            input_text += result.alternatives[0].transcript
        
        # 應用文字修正
        input_text = apply_text_corrections(input_text).strip()
        
        # 【關鍵優化】空內容判斷
        if not input_text or len(input_text) < 1:
            print(f"[{datetime.now()}] English recognition result is empty.")
            return JSONResponse({
                "input_text": "",
                "text": "",
                "conversation_id": conversation_id,
                "status": "empty"
            })

        print(f"[{datetime.now()}] 轉錄完成: {input_text}")
        
        # 呼叫英文 AI 聊天 API
        ai_url = "https://ddgsrvchat.aicreate360.com/custom_service_with_language?language=english"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJlbWFpbCI6ImFkbWluQGFpY3JlYXRlMzYwLmNvbSIsInJvbGUiOiJhZG1pbiIsImlhdCI6MTYwNjQ4NjU5Mn0.0j5z1E1l1z8Vr6ZtX9Dz4J6G1m6wD3jV5b8W7Xw5Y2c"
        }
        
        ai_payload = {
            "type": "message",
            "message": {
                "type": "text",
                "text": converter.convert(input_text)
            },
            "source": {
                "type": "user",
                "userId": "U03cd17c02ef4a297c2c2a910e5b6219f"
            }
        }
        
        print(f"[{datetime.now()}] 呼叫 AI 聊天機器人...")
        try:
            ai_response = await async_client.post(ai_url, headers=headers, json=ai_payload)
            if ai_response.status_code != 200:
                print(f"[{datetime.now()}] AI 伺服器回傳錯誤代碼: {ai_response.status_code}")
                message = "Sorry, the system is busy. Please try again later."
            else:
                ai_response_json = ai_response.json()
                message = ai_response_json.get('message', "I couldn't understand that.")
        except Exception as ai_err:
            print(f"[{datetime.now()}] 呼叫 AI 失敗: {str(ai_err)}")
            message = "Sorry, I am having some trouble. Please talk to me again."
        
        # 應用文字修正
        message = apply_text_corrections(message)
        
        return JSONResponse({
            "input_text": converter.convert(input_text),
            "text": converter.convert(message),
            "conversation_id": conversation_id,
            "status": "success"
        })
        
    except Exception as e:
        print(f"[{datetime.now()}] 轉錄錯誤: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ai_chat4")
async def ai_chat_zh(request: TextChatRequest):
    """中文純文字對話"""
    try:
        print(f"[{datetime.now()}] 中文文字對話: {request.text}")
        
        converted_input = converter.convert(request.text).strip()
        
        if not converted_input:
            return JSONResponse({
                "input_text": "",
                "text": "",
                "conversation_id": request.conversation_id,
                "status": "empty"
            })

        # 呼叫 AI 聊天 API
        ai_url = "https://cs01-line.ai360.workers.dev/api/chat"
        ai_payload = {
            "text": converted_input,
            "conversation_id": request.conversation_id,
            "notebook_id": "notebook:47rayc7fhfiower8b918"
        }
        
        try:
            ai_response = await async_client.post(ai_url, json=ai_payload)
            if ai_response.status_code != 200:
                print(f"[{datetime.now()}] AI 伺服器回傳錯誤代碼: {ai_response.status_code}")
                message = "抱歉，系統目前忙碌中，請稍後再試。"
            else:
                ai_response_json = ai_response.json()
                ai_messages = [msg for msg in ai_response_json['messages'] if msg['type'] == 'ai']
                message = ai_messages[-1]['content'] if ai_messages else "抱歉，我無法理解您的問題。"
        except Exception as ai_err:
            print(f"[{datetime.now()}] 呼叫 AI 失敗: {str(ai_err)}")
            message = "抱歉，我現在有點不舒服，請再對我說一次。"
        
        # 應用文字修正和替換
        message = apply_text_corrections(message)
        message = re.sub(r'\*+', '', message)
        
        return JSONResponse({
            "input_text": converter.convert(request.text),
            "text": converter.convert(message),
            "conversation_id": request.conversation_id,
            "status": "success"
        })
        
    except Exception as e:
        print(f"[{datetime.now()}] 對話錯誤: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ai_chat4_en")
async def ai_chat_en(request: TextChatRequest):
    """英文純文字對話"""
    try:
        print(f"[{datetime.now()}] 英文文字對話: {request.text}")
        
        converted_input = converter.convert(request.text).strip()
        
        if not converted_input:
            return JSONResponse({
                "input_text": "",
                "text": "",
                "conversation_id": request.conversation_id,
                "status": "empty"
            })

        # 呼叫英文 AI 聊天 API
        ai_url = "https://ddgsrvchat.aicreate360.com/custom_service_with_language?language=english"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJlbWFpbCI6ImFkbWluQGFpY3JlYXRlMzYwLmNvbSIsInJvbGUiOiJhZG1pbiIsImlhdCI6MTYwNjQ4NjU5Mn0.0j5z1E1l1z8Vr6ZtX9Dz4J6G1m6wD3jV5b8W7Xw5Y2c"
        }
        
        ai_payload = {
            "type": "message",
            "message": {
                "type": "text",
                "text": converted_input
            },
            "source": {
                "type": "user",
                "userId": "U03cd17c02ef4a297c2c2a910e5b6219f"
            }
        }
        
        try:
            ai_response = await async_client.post(ai_url, headers=headers, json=ai_payload)
            if ai_response.status_code != 200:
                print(f"[{datetime.now()}] AI 伺服器回傳錯誤代碼: {ai_response.status_code}")
                message = "Sorry, the system is busy. Please try again later."
            else:
                ai_response_json = ai_response.json()
                message = ai_response_json.get('message', "I couldn't understand that.")
        except Exception as ai_err:
            print(f"[{datetime.now()}] 呼叫 AI 失敗: {str(ai_err)}")
            message = "Sorry, I am having some trouble. Please talk to me again."
        
        # 應用文字修正
        message = apply_text_corrections(message)
        
        return JSONResponse({
            "input_text": converter.convert(request.text),
            "text": converter.convert(message),
            "conversation_id": request.conversation_id,
            "status": "success"
        })
        
    except Exception as e:
        print(f"[{datetime.now()}] 對話錯誤: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tts")
async def text_to_speech(request: TTSRequest):
    """
    將文字轉換為語音並返回完整的音檔
    """
    try:
        print(f'[{datetime.now()}] TTS Request - Text: {request.text[:50]}..., Voice: {request.voice}, Format: {request.format}')
        
        # 應用文字替換規則
        processed_text = apply_text_replacements(request.text)
        
        if request.format.lower() == "wav":
            media_type = "audio/wav"
            filename = "speech.wav"
        else:
            media_type = "audio/mpeg"
            filename = "speech.mp3"
        
        # 建立 communicate 物件
        communicate = edge_tts.Communicate(
            text=processed_text,
            voice=request.voice,
            rate=request.rate,
            volume=request.volume,
            pitch=request.pitch
        )
        
        # 收集所有音訊資料
        audio_data = BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data.write(chunk["data"])
        
        audio_data.seek(0)
        
        print(f'[{datetime.now()}] TTS Success - Generated {audio_data.getbuffer().nbytes} bytes ({request.format})')
        
        return Response(
            content=audio_data.read(),
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    
    except Exception as e:
        print(f'[{datetime.now()}] TTS Error: {str(e)}')
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    print(f"[{datetime.now()}] Starting MaxGut Unified API on port 3566...")
    uvicorn.run(app, host="0.0.0.0", port=3566)
