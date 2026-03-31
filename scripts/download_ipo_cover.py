# -*- coding: utf-8 -*-
"""
下载 IPO 文章封面图
文章：The plan to make IPOs great again
"""

import requests
from pathlib import Path

WORKSPACE = Path.home() / '.openclaw' / 'workspace'
TEMP_DIR = WORKSPACE / 'temp' / 'wechat_images'

# 封面图 URL
IMAGE_URL = "https://www.economist.com/cdn-cgi/image/width=1424,quality=80,format=auto/content-assets/images/20260328_WBP504.jpg"

def download_image():
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    
    # 使用浏览器 User-Agent
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        'Referer': 'https://www.economist.com/'
    }
    
    print(f"[INFO] 正在下载封面图：{IMAGE_URL}")
    response = requests.get(IMAGE_URL, headers=headers, timeout=60)
    response.raise_for_status()
    
    # 保存为 JPG（微信支持）
    from PIL import Image
    from io import BytesIO
    
    # 打开图片
    img = Image.open(BytesIO(response.content))
    
    # 转换为 RGB（确保没有透明通道）
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGB')
    
    # 保存为 JPG
    output_path = TEMP_DIR / "ipo_cover.jpg"
    img.save(output_path, 'JPEG', quality=95)
    
    print(f"[OK] 封面图已保存到：{output_path}")
    print(f"[SIZE] 文件大小：{len(response.content):,} bytes")
    print(f"[DIMENSIONS] 图片尺寸：{img.size[0]}x{img.size[1]}")
    
    return str(output_path)

if __name__ == '__main__':
    try:
        download_image()
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        exit(1)
