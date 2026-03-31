# -*- coding: utf-8 -*-
"""
直接从经济学人图片链接下载原图

使用方法：
1. 从文章页面获取图片 URL（浏览器工具或 JavaScript）
2. 更新 IMAGE_URL 变量
3. 运行：python download_cover_direct.py
4. 图片保存到：temp/wechat_images/cover_image.jpg

注意：
- 自动转换为 JPG 格式（微信支持）
- 保持原图尺寸，不裁剪
- 添加 User-Agent 和 Referer 绕过防盗链
"""

import requests
from pathlib import Path

WORKSPACE = Path.home() / '.openclaw' / 'workspace'
TEMP_DIR = WORKSPACE / 'temp' / 'wechat_images'

# 图片 URL（从文章页面获取的）
# 文章：China is winning the AI talent race
# 使用文章中的主图（金色大脑输送带）
IMAGE_URL = "https://www.economist.com/cdn-cgi/image/width=1424,quality=80,format=auto/content-assets/images/20260325_SCI001.jpg"

# 如果上面 URL 失败，使用备用方案：从浏览器截图提取
# 运行：python scripts/extract_cover_from_screenshot.py

def download_image():
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    
    # 使用浏览器 User-Agent
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        'Referer': 'https://www.economist.com/'
    }
    
    print(f"[INFO] 正在下载图片：{IMAGE_URL}")
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
    output_path = TEMP_DIR / "cover_image.jpg"
    img.save(output_path, 'JPEG', quality=95)
    
    print(f"[OK] 图片已保存到：{output_path}")
    print(f"[SIZE] 文件大小：{len(response.content):,} bytes")
    
    return str(output_path)

if __name__ == '__main__':
    try:
        download_image()
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        exit(1)
