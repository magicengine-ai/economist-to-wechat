# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
获取微信公众号 Access Token
"""

import requests
import json
import os
import time
from pathlib import Path

def load_credentials():
    """从配置文件或环境变量加载凭证"""
    # 优先从环境变量读取
    app_id = os.getenv('WECHAT_APP_ID')
    app_secret = os.getenv('WECHAT_APP_SECRET')
    
    if app_id and app_secret:
        return app_id, app_secret
    
    # 从配置文件读取
    config_path = Path.home() / '.openclaw' / 'workspace' / '.wechat-credentials.json'
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get('appId'), config.get('appSecret')
    
    raise ValueError("未找到微信凭证，请设置环境变量 WECHAT_APP_ID 和 WECHAT_APP_SECRET，或创建配置文件")

def get_access_token(app_id, app_secret):
    """获取 access_token"""
    url = "https://api.weixin.qq.com/cgi-bin/token"
    params = {
        "grant_type": "client_credential",
        "appid": app_id,
        "secret": app_secret
    }
    
    print(f"正在获取 access_token...")
    print(f"AppID: {app_id}")
    
    response = requests.get(url, params=params, timeout=10)
    result = response.json()
    
    if 'access_token' in result:
        print(f"[OK] 成功获取 access_token")
        print(f"Token: {result['access_token'][:20]}...")
        print(f"有效期：{result.get('expires_in', 7200)} 秒")
        return result['access_token']
    else:
        print(f"[FAIL] 获取失败：{result}")
        raise Exception(f"微信 API 错误：{result.get('errmsg', '未知错误')}")

def save_token(token, expires_in=7200):
    """保存 token 到缓存文件"""
    cache_path = Path.home() / '.openclaw' / 'workspace' / '.wechat-token-cache.json'
    cache_data = {
        'token': token,
        'expires_at': time.time() + expires_in - 300  # 提前 5 分钟过期
    }
    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f)
    print(f"Token 已缓存")

def main():
    try:
        app_id, app_secret = load_credentials()
        token = get_access_token(app_id, app_secret)
        save_token(token)
        print(f"\nToken: {token}")
    except Exception as e:
        print(f"错误：{e}")
        exit(1)

if __name__ == '__main__':
    main()
