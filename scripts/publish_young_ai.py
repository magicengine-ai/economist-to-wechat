#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发布年轻人 AI 文章到微信公众号
"""

import requests
import json
from pathlib import Path
import time

# 加载凭证
credentials_path = Path.home() / '.openclaw' / 'workspace' / '.wechat-credentials.json'
with open(credentials_path, 'r', encoding='utf-8') as f:
    config = json.load(f)
    app_id = config['appId']
    app_secret = config['appSecret']

print(f"公众号：{config.get('accountName', 'Unknown')}")

# 获取 token
url = f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={app_id}&secret={app_secret}'
resp = requests.get(url, timeout=10)
token_result = resp.json()
if 'access_token' not in token_result:
    print(f'获取 token 失败：{token_result}')
    exit(1)
    
token = token_result['access_token']
print(f'[OK] Token 获取成功')

# 缓存 token
cache_path = Path.home() / '.openclaw' / 'workspace' / '.wechat-token-cache.json'
cache_data = {
    'token': token,
    'expires_at': time.time() + token_result.get('expires_in', 7200) - 300
}
with open(cache_path, 'w', encoding='utf-8') as f:
    json.dump(cache_data, f)

# 上传封面图
cover_path = Path.home() / '.openclaw' / 'media' / 'browser' / 'cb178287-2cdb-47bc-ba24-1322d7cc4ebe.jpg'
if not cover_path.exists():
    print(f'封面图不存在：{cover_path}')
    exit(1)

print(f'上传封面图：{cover_path}')
upload_url = f'https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image'
with open(cover_path, 'rb') as f:
    files = {'media': f}
    upload_resp = requests.post(upload_url, files=files, timeout=30)
    
upload_result = upload_resp.json()
if 'media_id' not in upload_result:
    print(f'图片上传失败：{upload_result}')
    exit(1)

media_id = upload_result['media_id']
print(f'[OK] 封面图上传成功，media_id: {media_id}')

# 读取 HTML 内容
html_path = Path.home() / '.openclaw' / 'workspace' / 'temp' / 'wechat_output' / 'young_ai_final.html'
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

print(f'读取 HTML 内容：{html_path}')

# 创建草稿
title = '经济学人 | 年轻人如何使用 AI 比时长更重要 | How the young use AI matters'
draft_url = f'https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}'
draft_data = {
    'articles': [{
        'title': title,
        'content': content,
        'author': 'Sema Sgaier',
        'digest': '年轻人使用 AI 的方式比时长更重要',
        'thumb_media_id': media_id,
        'show_cover_pic': 1
    }]
}

print(f'创建草稿：{title}')
# 关键：使用 ensure_ascii=False 避免中文转义
draft_resp = requests.post(
    draft_url,
    data=json.dumps(draft_data, ensure_ascii=False).encode('utf-8'),
    headers={'Content-Type': 'application/json; charset=utf-8'},
    timeout=30
)
draft_result = draft_resp.json()

if draft_result.get('errcode', 0) == 0:
    print(f'[OK] 草稿创建成功！')
    print(f'Media ID: {draft_result.get("media_id")}')
    print(f'请登录公众号后台查看草稿箱')
    print(f'公众号：https://mp.weixin.qq.com')
else:
    print(f'[FAIL] 创建失败：{draft_result}')
    print(f'错误码：{draft_result.get("errcode")}')
    print(f'错误信息：{draft_result.get("errmsg")}')
