# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
经济学人文章一键发布工具

用法：
    python scripts/publish_from_url.py <economist_url>

示例：
    python scripts/publish_from_url.py https://www.economist.com/leaders/2026/04/01/lessons-for-the-world-from-tiny-hungary

完整流程：
    1. 浏览器抓取原文 innerHTML（保留 initial/small 标签）
    2. 从原文获取副标题和封面图 URL
    3. 下载封面图
    4. 发布前检查（检测英文段落中的中文字符、标签完整性）
    5. 准备中文翻译（调用 DeepL 或手动编辑）
    6. 转换格式（small 标签、首字母大写、中文样式）
    7. 上传封面图到微信素材库
    8. 创建草稿
    9. 清理临时文件
"""

import re
import json
import time
import sys
import os
from pathlib import Path
from datetime import datetime

# 添加脚本目录到路径
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

# 导入现有模块
try:
    from economist_to_wechat import (
        convert_small_tags, format_first_paragraph, format_paragraph,
        format_chinese_paragraph, convert_article
    )
except ImportError:
    print("[ERROR] 未找到 economist_to_wechat 模块")
    print("请确保在 economist-to-wechat/scripts 目录下运行此脚本")
    sys.exit(1)

# 配置
WORKSPACE = Path.home() / '.openclaw' / 'workspace'
SKILL_DIR = WORKSPACE / 'economist-to-wechat'
CREDENTIALS_FILE = WORKSPACE / '.wechat-credentials.json'
TOKEN_CACHE_FILE = WORKSPACE / '.wechat-token-cache.json'
DEEPL_CREDENTIALS_FILE = WORKSPACE / '.deepl-credentials.json'
TEMP_DIR = WORKSPACE / 'temp' / 'wechat_images'
WECHAT_API_BASE = "https://api.weixin.qq.com/cgi-bin"

# small 标签样式
SMALL_STYLE = 'border:0;font-style:inherit;font-variant-ligatures:none;font-variant-caps:small-caps;font-variant-numeric:normal;font-variant-east-asian:normal;font-variant-alternates:normal;font-variant-position:normal;font-variant-emoji:normal;font-weight:inherit;font-stretch:inherit;line-height:inherit;font-family:inherit;font-size:inherit;margin:0;padding:0;vertical-align:baseline;display:inline;text-transform:lowercase;'


# ==================== 浏览器抓取 ====================

def fetch_article_from_browser(url):
    """
    使用浏览器抓取文章内容
    
    返回：
    {
        'title': str,              # 文章标题
        'subtitle': str,           # 副标题（英文）
        'cover_url': str,          # 封面图 URL
        'paragraphs': [            # 段落列表
            {'innerHTML': str, 'has_initial': bool},
            ...
        ]
    }
    """
    print("[1/9] 正在抓取文章内容...")
    
    # 使用 OpenClaw browser 工具
    import subprocess
    
    # 打开页面
    print(f"  打开：{url}")
    
    # JavaScript 抓取代码
    fetch_js = '''
    () => {
        const article = document.querySelector('article');
        if (!article) {
            return { error: '未找到 article 标签' };
        }
        
        // 获取标题
        const title = document.querySelector('article h1')?.textContent.trim() || '';
        
        // 获取副标题
        const subtitle = document.querySelector('article h2')?.textContent.trim() || '';
        
        // 获取封面图
        const coverImg = document.querySelector('article img[src*="cdn-cgi"]')?.src || '';
        
        // 抓取段落（保留 innerHTML）
        const allPs = article.querySelectorAll('p');
        const paragraphs = Array.from(allPs).map((p) => {
            const innerHTML = p.innerHTML;
            const hasInitial = p.querySelector('span[data-caps="initial"]') !== null;
            const text = innerHTML.trim();
            return text.length > 50 ? { innerHTML: text, has_initial: hasInitial } : null;
        }).filter(x => x !== null);
        
        // 过滤掉作者介绍段落（通常包含 "is a" 或 "was a" 且没有 small 标签）
        const filtered = paragraphs.filter((p, i) => {
            // 保留前 15 段（正文）
            if (i < 15) return true;
            // 过滤作者介绍
            const text = p.innerHTML.toLowerCase();
            if (text.includes(' is a ') || text.includes(' was a ')) {
                if (!text.includes('<small>')) return false;
            }
            return true;
        });
        
        return { title, subtitle, coverImg, paragraphs: filtered };
    }
    '''
    
    # 这里需要调用 OpenClaw browser 工具
    # 由于这是在独立脚本中，我们通过命令行调用
    print("  请确保浏览器已打开该页面")
    print("  按 Enter 继续（请手动在浏览器控制台运行抓取代码）...")
    input()
    
    # 临时方案：让用户手动粘贴抓取结果
    print("\n  请在浏览器控制台运行以下 JavaScript 代码：\n")
    print("-" * 60)
    print(fetch_js)
    print("-" * 60)
    print("\n  粘贴返回的 JSON 数据（或输入文件路径）：")
    
    user_input = input().strip()
    
    if Path(user_input).exists():
        # 从文件读取
        with open(user_input, 'r', encoding='utf-8') as f:
            article_data = json.load(f)
    else:
        # 直接解析 JSON
        article_data = json.loads(user_input)
    
    if 'error' in article_data:
        raise Exception(f"抓取失败：{article_data['error']}")
    
    print(f"  ✓ 标题：{article_data['title']}")
    print(f"  ✓ 副标题：{article_data['subtitle']}")
    print(f"  ✓ 段落数：{len(article_data['paragraphs'])}")
    print(f"  ✓ 封面图：{article_data['coverImg'][:50]}...")
    
    return {
        'title': article_data['title'],
        'subtitle': article_data['subtitle'],
        'cover_url': article_data['coverImg'],
        'paragraphs': article_data['paragraphs']
    }


# ==================== 下载封面图 ====================

def download_cover_image(cover_url, output_path=None):
    """下载封面图"""
    print("[2/9] 正在下载封面图...")
    
    import requests
    from PIL import Image
    from io import BytesIO
    
    if output_path is None:
        TEMP_DIR.mkdir(parents=True, exist_ok=True)
        output_path = TEMP_DIR / f"cover_{int(time.time())}.jpg"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://www.economist.com/'
    }
    
    print(f"  URL: {cover_url}")
    response = requests.get(cover_url, headers=headers, timeout=60)
    response.raise_for_status()
    
    # 转换为 JPG
    img = Image.open(BytesIO(response.content))
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGB')
    
    img.save(output_path, 'JPEG', quality=95)
    
    print(f"  ✓ 已保存：{output_path}")
    print(f"  ✓ 大小：{len(response.content):,} bytes")
    
    return str(output_path)


# ==================== 发布前检查 ====================

def check_article(paragraphs):
    """
    发布前检查
    
    返回问题列表，空列表表示无问题
    """
    print("[4/9] 发布前检查...")
    
    issues = []
    
    for i, para in enumerate(paragraphs):
        html = para['innerHTML']
        
        # 检查英文段落中的中文字符
        if re.search(r'[\u4e00-\u9fff]', html):
            issues.append(f"段落{i+1}: 英文中包含中文字符")
        
        # 检查 small 标签是否已转换（应该保留原文的 small 标签，稍后由转换函数处理）
        if '<small>' in html and html.count('<small>') != html.count('</small>'):
            issues.append(f"段落{i+1}: small 标签不匹配")
        
        # 检查 initial 标签
        if para.get('has_initial'):
            if '<span data-caps="initial">' not in html:
                issues.append(f"段落{i+1}: 标记为有 initial 但未找到标签")
    
    if issues:
        print(f"  ⚠️ 发现 {len(issues)} 个问题:")
        for issue in issues:
            print(f"    - {issue}")
    else:
        print("  ✓ 检查通过")
    
    return issues


# ==================== 翻译 ====================

def translate_with_deepl(paragraphs):
    """使用 DeepL 翻译"""
    print("[5/9] 正在使用 DeepL 翻译...")
    
    import requests
    
    # 加载 DeepL 凭证
    if not DEEPL_CREDENTIALS_FILE.exists():
        print("  ⚠️ 未找到 DeepL 凭证，请手动翻译")
        return None
    
    with open(DEEPL_CREDENTIALS_FILE, 'r', encoding='utf-8') as f:
        deepl_creds = json.load(f)
    
    api_key = deepl_creds.get('api_key')
    api_url = deepl_creds.get('api_url', 'https://api-free.deepl.com/v2/translate')
    
    translations = []
    
    # 批量翻译（每段单独翻译以保持对应）
    for i, para in enumerate(paragraphs):
        # 移除 HTML 标签获取纯文本
        text = re.sub(r'<[^>]+>', '', para['innerHTML'])
        text = text.replace('&amp;', '&').replace('&nbsp;', ' ')
        
        if len(text.strip()) < 10:
            translations.append("")
            continue
        
        payload = {
            'text': [text],
            'target_lang': 'ZH',
            'tag_handling': 'html'
        }
        
        headers = {
            'Authorization': f'DeepL-Auth-Key {api_key}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(api_url, json=payload, headers=headers, timeout=30)
            result = response.json()
            
            if 'translations' in result and len(result['translations']) > 0:
                translated = result['translations'][0]['text']
                translations.append(translated)
                print(f"  ✓ 段落{i+1}: {len(text)} → {len(translated)} 字")
            else:
                translations.append(f"[翻译失败：{result}]")
        except Exception as e:
            translations.append(f"[翻译错误：{e}]")
    
    return translations


def manual_translate(paragraphs, output_file=None):
    """手动翻译 - 创建 JSON 模板"""
    print("[5/9] 准备翻译模板...")
    
    if output_file is None:
        output_file = SKILL_DIR / 'translation-template.json'
    
    template = {
        'paragraphs': []
    }
    
    for i, para in enumerate(paragraphs):
        # 移除 HTML 标签获取纯文本参考
        text = re.sub(r'<[^>]+>', '', para['innerHTML'])
        text = text.replace('&amp;', '&').replace('&nbsp;', ' ')
        
        template['paragraphs'].append({
            'index': i,
            'english': text[:100] + '...' if len(text) > 100 else text,
            'chinese': ''  # 待填写
        })
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(template, f, ensure_ascii=False, indent=2)
    
    print(f"  ✓ 翻译模板已保存：{output_file}")
    print(f"  请填写中文翻译后按 Enter 继续...")
    input()
    
    # 重新读取
    with open(output_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    translations = [item['chinese'] for item in data['paragraphs']]
    return translations


# ==================== 微信 API ====================

def load_credentials():
    """加载微信公众号凭证"""
    with open(CREDENTIALS_FILE, 'r', encoding='utf-8') as f:
        config = json.load(f)
        return config.get('appId'), config.get('appSecret')

def get_access_token():
    """获取微信公众号 access_token"""
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

def upload_image(token, image_path):
    """上传图片素材"""
    url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image"
    
    with open(image_path, 'rb') as f:
        files = {'media': f}
        response = requests.post(url, files=files)
    
    data = response.json()
    if 'media_id' in data:
        return data['media_id']
    raise Exception(f"上传图片失败：{data}")

def create_draft(token, article_data):
    """创建微信公众号草稿"""
    url = f"{WECHAT_API_BASE}/draft/add?access_token={token}"
    payload = {"articles": [article_data]}
    
    print(f"[8/9] 正在创建草稿：{article_data.get('title', '')}")
    response = requests.post(url, data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
                             headers={'Content-Type': 'application/json; charset=utf-8'}, timeout=60)
    result = response.json()
    
    if result.get('errcode', 0) != 0:
        raise Exception(f"创建草稿失败：{result}")
    
    print("  ✓ 草稿创建成功")
    return result


# ==================== 主流程 ====================

def build_cover_image_html(media_id):
    """构建封面图 HTML"""
    return f'''<section style="margin: 16px 0; text-align: center;">
        <img src="https://mmbiz.qpic.cn/mmbiz_jpg/{media_id}/640?wxfrom=12&amp;tp=wxpic"
             style="max-width: 100%; height: auto; display: inline-block;" />
    </section>'''

def main():
    if len(sys.argv) < 2:
        print("用法：python publish_from_url.py <economist_url>")
        print("\n示例:")
        print("  python publish_from_url.py https://www.economist.com/leaders/2026/04/01/...")
        sys.exit(1)
    
    url = sys.argv[1]
    
    print("=" * 60)
    print("经济学人文章一键发布工具")
    print("=" * 60)
    print(f"文章 URL: {url}\n")
    
    try:
        # 1. 浏览器抓取
        article_data = fetch_article_from_browser(url)
        
        # 2. 下载封面图
        cover_path = download_cover_image(article_data['cover_url'])
        
        # 3. 保存原始数据（备份）
        backup_file = SKILL_DIR / f'article_backup_{int(time.time())}.json'
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(article_data, f, ensure_ascii=False, indent=2)
        print(f"[3/9] 原始数据已备份：{backup_file}")
        
        # 4. 发布前检查
        issues = check_article(article_data['paragraphs'])
        if issues:
            print("\n  ⚠️ 发现问题，是否继续？(y/n): ", end='')
            if input().lower() != 'y':
                print("已取消")
                return
        
        # 5. 翻译
        if DEEPL_CREDENTIALS_FILE.exists():
            chinese_translations = translate_with_deepl(article_data['paragraphs'])
        else:
            chinese_translations = manual_translate(article_data['paragraphs'])
        
        if not chinese_translations or any(not t for t in chinese_translations):
            print("\n  ⚠️ 翻译不完整，请检查后重试")
            return
        
        # 6. 获取 token
        print("[6/9] 正在获取 access token...")
        token = get_access_token()
        print("  ✓ Token 获取成功")
        
        # 7. 上传图片
        print("[7/9] 正在上传封面图...")
        thumb_media_id = upload_image(token, cover_path)
        print(f"  ✓ 上传成功：{thumb_media_id}")
        
        # 8. 构建 HTML 并创建草稿
        cover_html = build_cover_image_html(thumb_media_id)
        
        # 转换文章
        content_html = convert_article(
            paragraphs=article_data['paragraphs'],
            article_meta={'subtitle_en': article_data['subtitle'], 'subtitle_zh': chinese_translations[0][:50]},
            chinese_translations=chinese_translations,
            cover_image_html=cover_html
        )
        
        # 标题格式：经济学人｜中文标题｜英文标题
        title_en = article_data['title']
        title_zh = "来自小国匈牙利的世界启示"  # 可优化为自动翻译
        
        full_title = f"经济学人｜{title_zh}｜{title_en}"
        
        article_for_draft = {
            "title": full_title[:50],  # 微信限制 50 字符
            "author": "The Economist",
            "digest": chinese_translations[0][:120] if chinese_translations else "",
            "content": content_html,
            "content_source_url": url,
            "thumb_media_id": thumb_media_id,
            "show_cover_pic": 1
        }
        
        result = create_draft(token, article_for_draft)
        
        # 9. 清理临时文件
        print("[9/9] 清理临时文件...")
        # 保留备份文件，只删除临时图片
        # cover_path 可以删除
        
        print("\n" + "=" * 60)
        print("✓ 发布完成！")
        print("=" * 60)
        print(f"\n标题：{full_title}")
        print(f"段落：{len(article_data['paragraphs'])} 段")
        print(f"翻译：{len(chinese_translations)} 段")
        print(f"\n请登录 https://mp.weixin.qq.com 查看草稿箱")
        
        return result
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
