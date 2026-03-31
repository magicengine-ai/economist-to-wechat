#!/usr/bin/env python3
"""
发布文章到微信公众号
"""

import requests
import json
import os
import sys
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
    
    raise ValueError("未找到微信凭�?)

def get_cached_token():
    """从缓存获�?token"""
    import time
    cache_path = Path.home() / '.openclaw' / 'workspace' / '.wechat-token-cache.json'
    if cache_path.exists():
        with open(cache_path, 'r', encoding='utf-8') as f:
            cache = json.load(f)
            if time.time() < cache.get('expires_at', 0):
                return cache.get('token')
    return None

def get_access_token(app_id, app_secret):
    """获取或刷�?access_token"""
    token = get_cached_token()
    if token:
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
    cache_path = Path.home() / '.openclaw' / 'workspace' / '.wechat-token-cache.json'
    import time
    cache_data = {
        'token': result['access_token'],
        'expires_at': time.time() + result.get('expires_in', 7200) - 300
    }
    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f)
    
    return result['access_token']

def create_draft(token, article):
    """创建草稿"""
    url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"
    
    payload = {
        "articles": [article]
    }
    
    print("正在创建草稿...")
    print(f"标题：{article.get('title', '无标�?)}")
    
    response = requests.post(url, json=payload, timeout=30)
    result = response.json()
    
    if result.get('errcode', 0) == 0:
        print(f"[OK] 草稿创建成功")
        print(f"Media ID: {result.get('media_id')}")
        return result
    else:
        print(f"[FAIL] 创建失败：{result}")
        raise Exception(f"微信 API 错误：{result.get('errmsg', '未知错误')}")

def publish_from_draft(token, media_id):
    """从草稿发�?""
    url = f"https://api.weixin.qq.com/cgi-bin/message/mass/sendall?access_token={token}"
    
    payload = {
        "filter": {
            "is_to_all": True
        },
        "mpnews": {
            "media_id": media_id
        },
        "msgtype": "mpnews"
    }
    
    print("正在发布文章...")
    
    response = requests.post(url, json=payload, timeout=30)
    result = response.json()
    
    if result.get('errcode', 0) == 0:
        print(f"[OK] 发布成功")
        print(f"消息 ID: {result.get('msg_id')}")
        return result
    else:
        print(f"[FAIL] 发布失败：{result}")
        raise Exception(f"微信 API 错误：{result.get('errmsg', '未知错误')}")

def main():
    if len(sys.argv) < 2:
        print("用法：python publish_article.py <article_json_file>")
        print("或：python publish_article.py --stdin")
        sys.exit(1)
    
    try:
        app_id, app_secret = load_credentials()
        token = get_access_token(app_id, app_secret)
        
        # 读取文章数据
        if sys.argv[1] == '--stdin':
            article = json.load(sys.stdin)
        else:
            with open(sys.argv[1], 'r', encoding='utf-8') as f:
                article = json.load(f)
        
        # 创建草稿
        draft_result = create_draft(token, article)
        draft_media_id = draft_result.get('media_id')
        
        # 询问是否立即发布
        print("\n是否立即群发�?y/n): ", end='')
        response = input()
        
        if response.lower() == 'y':
            publish_result = publish_from_draft(token, draft_media_id)
            print(f"\n发布完成！消�?ID: {publish_result.get('msg_id')}")
        else:
            print(f"\n草稿已保存，可在微信公众号后台手动发�?)
            print(f"草稿 Media ID: {draft_media_id}")
        
    except Exception as e:
        print(f"错误：{e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
