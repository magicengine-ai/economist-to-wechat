# -*- coding: utf-8 -*-
"""
下载 IPO 文章音频
文章：The plan to make IPOs great again
"""

import requests
from pathlib import Path

WORKSPACE = Path.home() / '.openclaw' / 'workspace'
TEMP_DIR = WORKSPACE / 'temp' / 'wechat_images'

# 音频 URL（从原文提取）
AUDIO_URL = "https://www.economist.com/content-assets/audio/text-to-speech/1e0fed19-7d12-40ff-a3fd-00297a051deb-a1b49b9ca574cc0549483ce4a5e1e1f3.mp3"

def download_audio():
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    
    # 使用浏览器 User-Agent
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'audio/mpeg,audio/*,*/*;q=0.8',
        'Referer': 'https://www.economist.com/'
    }
    
    print(f"[INFO] 正在下载音频：{AUDIO_URL}")
    response = requests.get(AUDIO_URL, headers=headers, timeout=120)
    response.raise_for_status()
    
    # 保存为 MP3
    output_path = TEMP_DIR / "ipo_audio.mp3"
    with open(output_path, 'wb') as f:
        f.write(response.content)
    
    print(f"[OK] 音频已保存到：{output_path}")
    print(f"[SIZE] 文件大小：{len(response.content):,} bytes ({len(response.content) / 1024 / 1024:.2f} MB)")
    
    return str(output_path)

if __name__ == '__main__':
    try:
        download_audio()
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        exit(1)
