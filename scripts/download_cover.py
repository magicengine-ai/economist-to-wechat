# -*- coding: utf-8 -*-
"""
下载经济学人文章主图并保存到本地
"""

import requests
from pathlib import Path

WORKSPACE = Path.home() / '.openclaw' / 'workspace'
TEMP_DIR = WORKSPACE / 'temp' / 'wechat_images'

# 图片 URL
IMAGE_URL = "https://www.economist.com/cdn-cgi/image/width=1424,quality=80,format=auto/content-assets/images/20260328_Scream_Smiley.jpg"

def download_image():
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    
    # 使用浏览�?User-Agent
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        'Referer': 'https://www.economist.com/'
    }
    
    print(f"[INFO] 正在下载图片：{IMAGE_URL}")
    response = requests.get(IMAGE_URL, headers=headers, timeout=60)
    response.raise_for_status()
    
    # 保存�?JPG
    output_path = TEMP_DIR / "cover_image.jpg"
    with open(output_path, 'wb') as f:
        f.write(response.content)
    
    print(f"[OK] 图片已保存到：{output_path}")
    print(f"[SIZE] 文件大小：{len(response.content)} bytes")
    
    return str(output_path)

if __name__ == '__main__':
    try:
        download_image()
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        exit(1)
