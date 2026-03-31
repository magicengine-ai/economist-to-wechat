# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
从经济学人网站抓取文章并转换为微信公众号格式
使用正则表达式解析，无需额外依赖
"""

import requests
import json
import time
import re
from pathlib import Path

# 配置
WORKSPACE = Path.home() / '.openclaw' / 'workspace'
CREDENTIALS_FILE = WORKSPACE / '.wechat-credentials.json'
TOKEN_CACHE_FILE = WORKSPACE / '.wechat-token-cache.json'
TEMP_DIR = WORKSPACE / 'temp' / 'wechat_images'
WECHAT_API_BASE = "https://api.weixin.qq.com/cgi-bin"

# 文章 URL
ARTICLE_URL = "https://www.economist.com/interactive/science-and-technology/2026/03/25/china-is-winning-the-ai-talent-race"

# 常见缩写词列表（自动检测并添加 <small>标签）
ABBREVIATIONS = [
    'AI', 'PR', 'STEM', 'GDP', 'CEO', 'CFO', 'COO', 'CTO', 'CIO',
    'IMF', 'OECD', 'WTO', 'UN', 'US', 'UK', 'EU', 'NATO', 'OPEC',
    'IRGC', 'NIOC', 'Basij', 'TS', 'NeurIPS', 'MIT', 'CV'
]

# 完整的 <small> 标签样式（来自 format-template.html 第一段）
SMALL_STYLE = 'border:0;font-style:inherit;font-variant-ligatures:none;font-variant-caps:small-caps;font-variant-numeric:normal;font-variant-east-asian:normal;font-variant-alternates:normal;font-variant-position:normal;font-variant-emoji:normal;font-weight:inherit;font-stretch:inherit;line-height:inherit;font-family:inherit;font-size:inherit;margin:0;padding:0;vertical-align:baseline;display:inline;text-transform:lowercase;'


def fetch_article_html(url):
    """从经济学人网站抓取文章 HTML"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.economist.com/'
    }
    
    response = requests.get(url, headers=headers, timeout=60)
    response.raise_for_status()
    
    return response.text


def parse_article(html):
    """解析文章 HTML，提取段落和元数据"""
    
    # 提取标题（h1 标签）
    h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
    title_en = ''
    if h1_match:
        # 移除标签内的 HTML
        title_en = re.sub(r'<[^>]+>', '', h1_match.group(1)).strip()
    
    # 提取副标题（h2 标签）
    h2_match = re.search(r'<h2[^>]*>(.*?)</h2>', html, re.DOTALL)
    subtitle_en = ''
    if h2_match:
        subtitle_en = re.sub(r'<[^>]+>', '', h2_match.group(1)).strip()
    
    # 提取所有 <p data-component="paragraph"> 标签
    # 使用正则表达式匹配段落
    para_pattern = r'<p[^>]*data-component="paragraph"[^>]*>(.*?)</p>'
    para_matches = re.findall(para_pattern, html, re.DOTALL)
    
    paragraphs = []
    
    for para_html in para_matches:
        # 检查是否有 initial 标签（首字母大写）
        has_initial = 'data-caps="initial"' in para_html
        
        # 提取 initial 标签内的首字母
        initial_letter = None
        if has_initial:
            initial_match = re.search(r'<span[^>]*data-caps="initial"[^>]*>(.*?)</span>', para_html, re.DOTALL)
            if initial_match:
                # 提取 <span leaf="">X</span> 中的 X
                letter_match = re.search(r'<span leaf="">([^<]+)</span>', initial_match.group(1))
                if letter_match:
                    initial_letter = letter_match.group(1)
        
        # 提取段落纯文本
        para_text = re.sub(r'<[^>]+>', '', para_html).strip()
        
        paragraphs.append({
            'text': para_text,
            'has_initial': has_initial,
            'initial_letter': initial_letter,
            'original_html': para_html
        })
    
    article_meta = {
        'title_en': title_en,
        'title_zh': '',
        'subtitle_en': subtitle_en,
        'subtitle_zh': '',
        'source_url': ARTICLE_URL
    }
    
    return article_meta, paragraphs


def wrap_abbreviations(text):
    """将文本中的缩写词用带完整样式的 <small>标签包裹"""
    result = text
    for abbr in ABBREVIATIONS:
        pattern = r'\b' + abbr + r'\b'
        replacement = r'<small style="' + SMALL_STYLE + r'"><span leaf="">' + abbr + r'</span></small>'
        result = re.sub(pattern, replacement, result)
    return result


def format_first_paragraph(para_text):
    """格式化第一段（带首字母大写）"""
    # 找到第一个字母作为首字母（跳过引号等非字母字符）
    first_letter = ''
    first_letter_idx = 0
    for idx, char in enumerate(para_text):
        if char.isalpha():
            first_letter = char
            first_letter_idx = idx
            break
    
    if not first_letter:
        return f'<p data-component="paragraph" style="border:0;font-style:normal;font-variant:oldstyle-nums;font-weight:400;font-stretch:inherit;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;margin:0;padding:0;color:rgb(13,13,13);text-align:start;"><span leaf="">{para_text}</span></p>'
    
    # 分离首字母前的内容、首字母、第一个单词剩余部分、剩余文本
    prefix = para_text[:first_letter_idx]
    rest_after_first = para_text[first_letter_idx + 1:]
    
    # 找到第一个空格，分离第一个单词和剩余文本
    first_space_idx = rest_after_first.find(' ')
    if first_space_idx > 0:
        first_word = rest_after_first[:first_space_idx]
        rest_text = rest_after_first[first_space_idx + 1:]
    else:
        first_word = rest_after_first
        rest_text = ""
    
    # 构建 HTML
    html = f'{prefix}<span data-caps="initial" style="border:0;font-style:inherit;font-variant:inherit;font-weight:inherit;font-stretch:inherit;line-height:1;font-family:inherit;font-size:3.5rem;margin:0 0.2rem 0 0;padding:0;vertical-align:baseline;float:left;height:3.25rem;text-transform:uppercase;"><span leaf="">{first_letter}</span></span>'
    html += f'<small style="{SMALL_STYLE}"><span leaf="">{first_word}</span></small>'
    html += f'<span leaf="">&nbsp;{rest_text}</span>'
    
    return f'<p data-component="paragraph" style="border:0;font-style:normal;font-variant:oldstyle-nums;font-weight:400;font-stretch:inherit;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;margin:0;padding:0;color:rgb(13,13,13);text-align:start;">{html}</span></p>'


def format_paragraph(para_text, is_first_with_initial=False):
    """格式化普通段落"""
    # 处理缩写词
    para_processed = wrap_abbreviations(para_text)
    
    if is_first_with_initial:
        return format_first_paragraph(para_processed)
    else:
        return f'<p data-component="paragraph" style="border:0;font-style:normal;font-variant:oldstyle-nums;font-weight:400;font-stretch:inherit;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;margin:0.875rem 0 0;padding:0;color:rgb(13,13,13);text-align:start;"><span leaf="" style="color:rgb(13,13,13);font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;font-style:normal;font-variant-ligatures:normal;font-variant-caps:normal;font-weight:400;letter-spacing:normal;text-align:start;text-indent:0px;text-transform:none;-webkit-text-stroke-width:0px;background-color:rgb(255,255,255);float:none;display:inline!important;">{para_processed}</span></p>'


def main():
    print("=" * 60)
    print("从经济学人网站抓取文章并生成 HTML")
    print("=" * 60)
    
    # 抓取文章
    print(f"\n[INFO] 正在抓取文章：{ARTICLE_URL}")
    html = fetch_article_html(ARTICLE_URL)
    
    # 解析文章
    print("[INFO] 正在解析文章...")
    article_meta, paragraphs = parse_article(html)
    
    print(f"[OK] 提取到 {len(paragraphs)} 个段落")
    print(f"[INFO] 带 initial 标签的段落：{sum(1 for p in paragraphs if p['has_initial'])}")
    
    # 构建 HTML
    print("[INFO] 构建 HTML...")
    html_parts = []
    
    # 副标题（英文）
    if article_meta['subtitle_en']:
        html_parts.append(f'<h1 style="border:0;font-style:normal;font-variant:oldstyle-nums;font-weight:400;font-stretch:inherit;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;margin:0;padding:0;color:rgb(13,13,13);text-align:start;"><span leaf="">{article_meta["subtitle_en"]}</span></h1>')
    
    # 副标题（中文）- 需要手动翻译
    html_parts.append(f'<p style="border:0;font-style:normal;font-variant:oldstyle-nums;font-weight:400;font-stretch:inherit;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;margin:0 0 8px;padding:0;color:rgb(13,13,13);text-align:start;"><span leaf="" style="border:0;font-variant-alternates:inherit;font-variant-numeric:inherit;font-variant-east-asian:inherit;font-variant-position:inherit;font-variant-emoji:inherit;font-stretch:inherit;line-height:inherit;font-optical-sizing:inherit;font-size-adjust:inherit;font-kerning:inherit;font-feature-settings:inherit;font-variation-settings:inherit;font-language-override:inherit;margin:0;padding:0;vertical-align:baseline;color:rgb(24,32,38);font-size:14px;" segoe="segoe" ui="ui" sans="sans" neue="neue">其对西方的领先优势只会不断扩大</span></p>')
    
    # 处理段落
    first_initial_found = False
    for i, para in enumerate(paragraphs):
        if para['has_initial'] and not first_initial_found:
            # 第一个带 initial 的段落 - 使用首字母大写格式
            html_parts.append(format_first_paragraph(para['text']))
            first_initial_found = True
            print(f"[INFO] 段落 {i+1}: 使用首字母大写格式 (首字母：{para['initial_letter']})")
        else:
            # 普通段落
            html_parts.append(format_paragraph(para['text']))
            print(f"[INFO] 段落 {i+1}: 普通格式")
        
        # 添加中文翻译占位（需要手动翻译）
        html_parts.append(f'<p style="border:0;font-style:normal;font-variant:oldstyle-nums;font-weight:400;font-stretch:inherit;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;margin:8px 0 16px;padding:0;color:rgb(13,13,13);text-align:start;"><span leaf="" style="border:0;font-variant-alternates:inherit;font-variant-numeric:inherit;font-variant-east-asian:inherit;font-variant-position:inherit;font-variant-emoji:inherit;font-stretch:inherit;line-height:inherit;font-optical-sizing:inherit;font-size-adjust:inherit;font-kerning:inherit;font-feature-settings:inherit;font-variation-settings:inherit;font-language-override:inherit;margin:0;padding:0;vertical-align:baseline;color:rgb(24,32,38);font-size:14px;" segoe="segoe" ui="ui" sans="sans" neue="neue">[中文翻译待添加]</span></p>')
    
    # 结束符号
    html_parts.append('<p style="display:none;"><mp-style-type data-value="10000"></mp-style-type></p>')
    
    # 保存 HTML 文件
    output_dir = WORKSPACE / 'temp' / 'wechat_output'
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'economist_auto.html'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('<!DOCTYPE html>\n')
        f.write('<html>\n')
        f.write('<head>\n')
        f.write('  <meta charset="UTF-8">\n')
        f.write(f'  <title>经济学人 - {article_meta["title_en"]}</title>\n')
        f.write('</head>\n')
        f.write('<body>\n')
        f.write('\n'.join(html_parts))
        f.write('\n</body>\n')
        f.write('</html>\n')
    
    print(f"\n[OK] HTML 文件已保存到：{output_file}")
    print(f"[INFO] 文件大小：{output_file.stat().st_size} bytes")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        exit(1)
