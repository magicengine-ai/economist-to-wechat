# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
从经济学人网站下载文章图�?"""

import requests
import re
import os
from pathlib import Path
from urllib.parse import urljoin

# 输出目录
OUTPUT_DIR = Path.home() / '.openclaw' / 'workspace' / 'temp' / 'economist_images'


def download_images(article_url, output_dir=None):
    """从经济学人文章下载所有图�?""
    if output_dir:
        output_dir = Path(output_dir)
    else:
        output_dir = OUTPUT_DIR
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 获取文章内容
    print(f"[INFO] 正在获取文章：{article_url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(article_url, headers=headers, timeout=30)
    response.raise_for_status()
    
    html = response.text
    
    # 提取图片 URL
    img_pattern = r'<img[^>]*src="([^"]+economist\.com[^"]+)"'
    img_urls = re.findall(img_pattern, html)
    
    # 去重
    img_urls = list(dict.fromkeys(img_urls))
    
    print(f"[INFO] 找到 {len(img_urls)} 张图�?)
    
    # 下载图片
    downloaded = []
    for i, img_url in enumerate(img_urls, 1):
        try:
            # 提取文件�?            img_name = os.path.basename(img_url.split('?')[0])
            if not img_name.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                img_name = f"image_{i}.jpg"
            
            output_path = output_dir / img_name
            
            # 下载
            print(f"[INFO] 下载图片 {i}/{len(img_urls)}: {img_url[:80]}...")
            img_response = requests.get(img_url, headers=headers, timeout=30)
            img_response.raise_for_status()
            
            # 保存
            with open(output_path, 'wb') as f:
                f.write(img_response.content)
            
            print(f"[OK] 已保存：{output_path}")
            downloaded.append(str(output_path))
            
        except Exception as e:
            print(f"[WARN] 下载失败 {img_url}: {e}")
    
    print(f"\n[完成] 共下�?{len(downloaded)} 张图�?)
    return downloaded


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("用法：python download_images.py <经济学人文章 URL> [输出目录]")
        print("示例：python download_images.py https://www.economist.com/business/2026/03/26/...")
        sys.exit(1)
    
    article_url = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    download_images(article_url, output_dir)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[WARN] 用户取消")
        exit(0)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        exit(1)
