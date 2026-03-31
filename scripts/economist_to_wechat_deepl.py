# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
经济学人文章转微信公众号格式 - DeepL 翻译�?
使用方法�?1. 设置 DeepL API 密钥�?env:DEEPL_API_KEY="your-api-key"
2. 运行脚本：python economist_to_wechat_deepl.py <文章 URL>
"""

import requests
import json
import time
import sys
from pathlib import Path

# 配置
WORKSPACE = Path.home() / '.openclaw' / 'workspace'
CREDENTIALS_FILE = WORKSPACE / '.wechat-credentials.json'
TOKEN_CACHE_FILE = WORKSPACE / '.wechat-token-cache.json'
TEMP_DIR = WORKSPACE / 'temp' / 'wechat_images'
WECHAT_API_BASE = "https://api.weixin.qq.com/cgi-bin"

# DeepL 配置
DEEPL_API_KEY = ''
DEEPL_API_URL = "https://api-free.deepl.com/v2/translate"


def translate_with_deepl(text):
    """使用 DeepL 翻译"""
    if not DEEPL_API_KEY:
        raise Exception("未设�?DeepL API 密钥")
    
    headers = {
        'Authorization': f'DeepL-Auth-Key {DEEPL_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'text': [text],
        'target_lang': 'ZH',
        'source_lang': 'EN'
    }
    
    response = requests.post(DEEPL_API_URL, headers=headers, json=payload, timeout=30)
    result = response.json()
    
    if 'translations' not in result:
        raise Exception(f"DeepL 翻译失败：{result}")
    
    return result['translations'][0]['text']


def load_credentials():
    with open(CREDENTIALS_FILE, 'r', encoding='utf-8') as f:
        config = json.load(f)
        return config.get('appId'), config.get('appSecret')


def get_access_token():
    if TOKEN_CACHE_FILE.exists():
        with open(TOKEN_CACHE_FILE, 'r', encoding='utf-8') as f:
            cache = json.load(f)
            if time.time() < cache.get('expires_at', 0):
                return cache.get('token')
    
    app_id, app_secret = load_credentials()
    url = f"{WECHAT_API_BASE}/token"
    params = {"grant_type": "client_credential", "appid": app_id, "secret": app_secret}
    
    response = requests.get(url, params=params, timeout=10)
    result = response.json()
    
    if 'access_token' not in result:
        raise Exception(f"获取 token 失败：{result}")
    
    token = result['access_token']
    expires_in = result.get('expires_in', 7200)
    
    with open(TOKEN_CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump({'token': token, 'expires_at': time.time() + expires_in - 300}, f)
    
    return token


def download_file(url, save_path):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    response = requests.get(url, headers=headers, timeout=60)
    response.raise_for_status()
    
    with open(save_path, 'wb') as f:
        f.write(response.content)
    
    return save_path


def upload_image(token, image_path):
    url = f"{WECHAT_API_BASE}/material/add_material?access_token={token}&type=image"
    
    with open(image_path, 'rb') as f:
        files = {'media': f}
        response = requests.post(url, files=files, timeout=60)
    
    result = response.json()
    
    if result.get('errcode', 0) != 0:
        raise Exception(f"上传图片失败：{result}")
    
    return {'media_id': result.get('media_id'), 'url': result.get('url', '')}


def build_article_content(article_meta, english_paragraphs, chinese_paragraphs, media_ids):
    """构建文章内容"""
    parts = []
    
    # 1. 副标题（英文�?    parts.append('<h1 style="border:0;font-style:normal;font-variant:oldstyle-nums;font-weight:400;font-stretch:inherit;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;margin:0;padding:0;color:rgb(13,13,13);text-align:start;"><span leaf="">{0}</span></h1>'.format(article_meta['subtitle_en']))
    
    # 2. 副标题（中文�?    parts.append('<p style="border:0;font-style:normal;font-variant:oldstyle-nums;font-weight:400;font-stretch:inherit;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;margin:0 0 8px;padding:0;color:rgb(13,13,13);text-align:start;"><span leaf="" style="border:0;font-variant-alternates:inherit;font-variant-numeric:inherit;font-variant-east-asian:inherit;font-variant-position:inherit;font-variant-emoji:inherit;font-stretch:inherit;line-height:inherit;font-optical-sizing:inherit;font-size-adjust:inherit;font-kerning:inherit;font-feature-settings:inherit;font-variation-settings:inherit;font-language-override:inherit;margin:0;padding:0;vertical-align:baseline;color:rgb(24,32,38);font-size:14px;" segoe="segoe" ui="ui" sans="sans" neue="neue">{0}</span></p>'.format(article_meta['subtitle_zh']))
    
    # 3. 主图
    if media_ids and media_ids[0]:
        parts.append('<section style="text-align:center;" nodeleaf=""><img class="rich_pages wxw-img" data-src="{0}" data-type="png" type="block"></section>'.format(media_ids[0]['url']))
    
    # 4. 正文段落
    for i, (en_para, zh_para) in enumerate(zip(english_paragraphs, chinese_paragraphs)):
        # 首字母大写样式（仅第一段）
        if i == 0:
            # 提取第一个字母和第一个词
            first_letter = en_para[0] if en_para else ''
            words = en_para.split(' ', 1)
            first_word = words[0][1:] if len(words) > 0 else ''
            rest_text = words[1] if len(words) > 1 else ''
            
            parts.append('<p data-component="paragraph" style="border:0;font-style:normal;font-variant:oldstyle-nums;font-weight:400;font-stretch:inherit;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;margin:0;padding:0;color:rgb(13,13,13);text-align:start;"><span data-caps="initial" style="border:0;font-style:inherit;font-variant:inherit;font-weight:inherit;font-stretch:inherit;line-height:1;font-family:inherit;font-size:3.5rem;margin:0 0.2rem 0 0;padding:0;vertical-align:baseline;float:left;height:3.25rem;text-transform:uppercase;"><span leaf="">{0}</span></span><small style="border:0;font-style:inherit;font-variant-ligatures:none;font-variant-caps:small-caps;font-variant-numeric:normal;font-variant-east-asian:normal;font-variant-alternates:normal;font-variant-position:normal;font-variant-emoji:normal;font-weight:inherit;font-stretch:inherit;line-height:inherit;font-family:inherit;font-size:inherit;margin:0;padding:0;vertical-align:baseline;display:inline;text-transform:lowercase;"><span leaf="">{1}</span></small><span leaf="">&nbsp;{2}</span></p>'.format(first_letter, first_word, rest_text))
        else:
            parts.append('<p data-component="paragraph" style="border:0;font-style:normal;font-variant:oldstyle-nums;font-weight:400;font-stretch:inherit;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;margin:0.875rem 0 0;padding:0;color:rgb(13,13,13);text-align:start;"><span leaf="" style="color:rgb(13,13,13);font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;font-style:normal;font-variant-ligatures:normal;font-variant-caps:normal;font-weight:400;letter-spacing:normal;text-align:start;text-indent:0px;text-transform:none;-webkit-text-stroke-width:0px;background-color:rgb(255,255,255);float:none;display:inline!important;">{0}</span></p>'.format(en_para))
        
        # 中文翻译
        zh_text = zh_para
        # 最后一段添加结束符�?        if i == len(chinese_paragraphs) - 1:
            zh_text += '�?
        
        parts.append('<p style="border:0;font-style:normal;font-variant:oldstyle-nums;font-weight:400;font-stretch:inherit;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;margin:8px 0 16px;padding:0;color:rgb(13,13,13);text-align:start;"><span leaf="" style="border:0;font-variant-alternates:inherit;font-variant-numeric:inherit;font-variant-east-asian:inherit;font-variant-position:inherit;font-variant-emoji:inherit;font-stretch:inherit;line-height:inherit;font-optical-sizing:inherit;font-size-adjust:inherit;font-kerning:inherit;font-feature-settings:inherit;font-variation-settings:inherit;font-language-override:inherit;margin:0;padding:0;vertical-align:baseline;color:rgb(24,32,38);font-size:14px;" segoe="segoe" ui="ui" sans="sans" neue="neue">{0}</span></p>'.format(zh_text))
        
        # 在第 3 段后插入图表
        if i == 2 and media_ids and len(media_ids) > 1 and media_ids[1]:
            parts.append('<section style="text-align:center;" nodeleaf=""><img class="rich_pages wxw-img" data-src="{0}" data-type="png" type="block"></section>'.format(media_ids[1]['url']))
    
    # 5. 隐藏样式标签
    parts.append('<p style="display: none;"><mp-style-type data-value="10000"></mp-style-type></p>')
    
    return ''.join(parts)


def create_draft(token, article_data):
    url = "{0}/draft/add?access_token={1}".format(WECHAT_API_BASE, token)
    payload = {"articles": [article_data]}
    
    print("[INFO] 正在创建草稿：{0}".format(article_data.get('title', '')))
    response = requests.post(url, data=json.dumps(payload, ensure_ascii=False).encode('utf-8'), 
                             headers={'Content-Type': 'application/json; charset=utf-8'}, timeout=60)
    result = response.json()
    
    if result.get('errcode', 0) != 0:
        raise Exception("创建草稿失败：{0}".format(result))
    
    print("[OK] 草稿创建成功")
    return result


def main():
    print("=" * 60)
    print("经济学人文章转微信公众号（DeepL 翻译版）")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        print("用法：python economist_to_wechat_deepl.py <文章 URL>")
        print("示例：python economist_to_wechat_deepl.py https://www.economist.com/...")
        sys.exit(1)
    
    article_url = sys.argv[1]
    
    # 检�?DeepL API 密钥
    global DEEPL_API_KEY
    DEEPL_API_KEY = ''  # 需要从环境变量或配置文件读�?    
    if not DEEPL_API_KEY:
        print("[ERROR] 未设�?DeepL API 密钥")
        print("请设置环境变量：$env:DEEPL_API_KEY='your-api-key'")
        sys.exit(1)
    
    print("[INFO] 文章 URL: {0}".format(article_url))
    print("[WARN] 注意：此脚本需要配合浏览器工具使用来抓取内�?)
    print("[INFO] 请使�?browser 工具打开文章页面，然后提取内�?)
    
    # 这里需要配�?browser 工具使用
    # 由于无法直接在此调用 browser 工具，需要用户提供内容或修改为交互式
    
    print("\n[INFO] 由于需要浏览器抓取，请使用以下步骤�?)
    print("1. �?browser 工具打开文章 URL")
    print("2. 提取标题、副标题、正文段落、图�?)
    print("3. 使用 DeepL 翻译正文")
    print("4. 调用此脚本发�?)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[WARN] 用户取消")
        exit(0)
    except Exception as e:
        print("\n[ERROR] {0}".format(e))
        import traceback
        traceback.print_exc()
        exit(1)
