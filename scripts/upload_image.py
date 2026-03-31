# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
上传图片素材到微信公众号
"""

import requests
import json
import os
import sys
import time
from pathlib import Path

def load_credentials():
    """加载微信凭证"""
    app_id = os.getenv('WECHAT_APP_ID')
    app_secret = os.getenv('WECHAT_APP_SECRET')
    
    if app_id and app_secret:
        return app_id, app_secret
    
    config_path = Path.home() / '.openclaw' / 'workspace' / '.wechat-credentials.json'
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get('appId'), config.get('appSecret')
    
    raise ValueError("未找到微信凭证")

def get_cached_token():
    """从缓存获取 token"""
    cache_path = Path.home() / '.openclaw' / 'workspace' / '.wechat-token-cache.json'
    if cache_path.exists():
        with open(cache_path, 'r', encoding='utf-8') as f:
            cache = json.load(f)
            if time.time() < cache.get('expires_at', 0):
                return cache.get('token')
    return None

def get_access_token(app_id, app_secret):
    """获取或刷新 access_token"""
    token = get_cached_token()
    if token:
        print("使用缓存的 access_token")
        return token
    
    url = "https://api.weixin.qq.com/cgi-bin/token"
    params = {
        "grant_type": "client_credential",
        "appid": app_id,
        "secret": app_secret
    }
    response = requests.get(url, params=params, timeout=10)
    result = response.json()
    
    if 'access_token' not in result:
        raise Exception(f"获取 token 失败：{result}")
    
    # 缓存 token
    save_token(result['access_token'], result.get('expires_in', 7200))
    
    return result['access_token']

def save_token(token, expires_in):
    """缓存 token"""
    cache_path = Path.home() / '.openclaw' / 'workspace' / '.wechat-token-cache.json'
    cache = {
        'token': token,
        'expires_at': time.time() + expires_in - 300  # 提前 5 分钟过期
    }
    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump(cache, f)

def upload_image(token, image_path):
    """上传图片素材"""
    url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image"
    
    # 检查文件大小
    file_size = os.path.getsize(image_path)
    if file_size > 2 * 1024 * 1024:
        print(f"警告：图片大小 {file_size/1024/1024:.2f}MB 超过 2MB 限制")
    
    print(f"正在上传图片：{image_path}")
    
    with open(image_path, 'rb') as f:
        files = {'media': f}
        response = requests.post(url, files=files, timeout=30)
    
    result = response.json()
    
    if result.get('errcode', 0) == 0:
        print(f"[OK] 上传成功")
        print(f"Media ID: {result.get('media_id')}")
        print(f"URL: {result.get('url')}")
        return result.get('media_id')
    else:
        print(f"[FAIL] 上传失败：{result}")
        raise Exception(f"微信 API 错误：{result.get('errmsg', '未知错误')}")

def download_image_from_url(url, save_path):
    """从 URL 下载图片"""
    print(f"下载图片：{url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    
    with open(save_path, 'wb') as f:
        f.write(response.content)
    
    print(f"已保存")
    return save_path

def main():
    if len(sys.argv) < 2:
        print("用法：python upload_image.py <image_path_or_url>")
        print("示例：python upload_image.py C:\\path\\to\\image.jpg")
        print("      python upload_image.py https://example.com/image.jpg")
        sys.exit(1)
    
    source = sys.argv[1]
    
    try:
        app_id, app_secret = load_credentials()
        token = get_access_token(app_id, app_secret)
        
        # 如果是 URL，先下载
        if source.startswith('http'):
            temp_dir = Path.home() / '.openclaw' / 'workspace' / 'temp'
            temp_dir.mkdir(exist_ok=True)
            temp_path = temp_dir / f"temp_image_{os.path.basename(source)}"
            download_image_from_url(source, str(temp_path))
            source = str(temp_path)
        
        media_id = upload_image(token, source)
        print(f"\nMedia ID: {media_id}")
        
    except Exception as e:
        print(f"错误：{e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
