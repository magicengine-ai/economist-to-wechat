# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
经济学人文章转换为微信公众号格式
核心规则：
1. 从原文提取 innerHTML（保留原文 small 标签的位置）
2. 根据原文 initial 标签判断首字母大写
3. 将原文的 <small> 标签转换为微信公众号格式（带完整样式 + <span leaf="">）
"""

import re
import json
import time
import requests
from pathlib import Path

# 配置
WORKSPACE = Path.home() / '.openclaw' / 'workspace'
CREDENTIALS_FILE = WORKSPACE / '.wechat-credentials.json'
TOKEN_CACHE_FILE = WORKSPACE / '.wechat-token-cache.json'
TEMP_DIR = WORKSPACE / 'temp' / 'wechat_images'
WECHAT_API_BASE = "https://api.weixin.qq.com/cgi-bin"

# small 标签完整样式
SMALL_STYLE = 'border:0;font-style:inherit;font-variant-ligatures:none;font-variant-caps:small-caps;font-variant-numeric:normal;font-variant-east-asian:normal;font-variant-alternates:normal;font-variant-position:normal;font-variant-emoji:normal;font-weight:inherit;font-stretch:inherit;line-height:inherit;font-family:inherit;font-size:inherit;margin:0;padding:0;vertical-align:baseline;display:inline;text-transform:lowercase;'


def convert_small_tags(inner_html):
    """
    将原文的 <small> 标签转换为微信公众号格式
    
    Args:
        inner_html: 原文的 innerHTML（包含 <small> 标签）
    
    Returns:
        转换后的 HTML（small 标签带完整样式 + <span leaf="">）
    """
    # 移除 HTML 注释
    html = re.sub(r'<!--.*?-->', '', inner_html, flags=re.DOTALL)
    
    # 移除 <i> 标签（微信不支持）
    html = html.replace('<i>', '').replace('</i>', '')
    
    # 替换 &amp; 为 &（避免重复转义）
    html = html.replace('&amp;', '&')
    
    # 将原文的 <small> 标签转换为微信公众号格式
    # 原文：<small>AI</small>
    # 转换后：<small style="完整样式"><span leaf="">AI</span></small>
    def replace_small(match):
        content = match.group(1)
        return f'<small style="{SMALL_STYLE}"><span leaf="">{content}</span></small>'
    
    html = re.sub(r'<small>(.*?)</small>', replace_small, html)
    
    # 替换结束符号（原文可能是 <span class="ufinish">■</span> 或其他格式）
    html = re.sub(r'<span[^>]*class="ufinish"[^>]*>■</span>', '<span style="color:rgb(227,18,11)">■</span>', html)
    
    return html


def format_first_paragraph(inner_html):
    """
    格式化第一段（带首字母大写）
    
    Args:
        inner_html: 原文的 innerHTML（包含 <span data-caps="initial"> 和 <small> 标签）
    
    Returns:
        格式化后的 HTML
    """
    # 转换 small 标签
    html = convert_small_tags(inner_html)
    
    # 替换 initial span 的样式
    html = html.replace(
        '<span data-caps="initial">',
        '<span data-caps="initial" style="border:0;font-style:inherit;font-variant:inherit;font-weight:inherit;font-stretch:inherit;line-height:1;font-family:inherit;font-size:3.5rem;margin:0 0.2rem 0 0;padding:0;vertical-align:baseline;float:left;height:3.25rem;text-transform:uppercase;">'
    )
    
    return f'<p data-component="paragraph" style="border:0;font-style:normal;font-variant:oldstyle-nums;font-weight:400;font-stretch:inherit;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;margin:0;padding:0;color:rgb(13,13,13);text-align:start;">{html}</p>'


def format_paragraph(inner_html):
    """
    格式化普通段落（转换原文的 small 标签）
    
    Args:
        inner_html: 原文的 innerHTML（包含 <small> 标签）
    
    Returns:
        格式化后的 HTML
    """
    # 转换 small 标签
    html = convert_small_tags(inner_html)
    
    return f'<p data-component="paragraph" style="border:0;font-style:normal;font-variant:oldstyle-nums;font-weight:400;font-stretch:inherit;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;margin:0.875rem 0 0;padding:0;color:rgb(13,13,13);text-align:start;"><span leaf="" style="color:rgb(13,13,13);font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;font-style:normal;font-variant-ligatures:normal;font-variant-caps:normal;font-weight:400;letter-spacing:normal;text-align:start;text-indent:0px;text-transform:none;-webkit-text-stroke-width:0px;background-color:rgb(255,255,255);float:none;display:inline!important;">{html}</span></p>'


def format_chinese_paragraph(text):
    """
    格式化中文段落
    
    Args:
        text: 中文文本
    
    Returns:
        格式化后的 HTML
    """
    return f'<p style="border:0;font-style:normal;font-variant:oldstyle-nums;font-weight:400;font-stretch:inherit;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;margin:8px 0 16px;padding:0;color:rgb(13,13,13);text-align:start;"><span leaf="" style="border:0;font-variant-alternates:inherit;font-variant-numeric:inherit;font-variant-east-asian:inherit;font-variant-position:inherit;font-variant-emoji:inherit;font-stretch:inherit;line-height:inherit;font-optical-sizing:inherit;font-size-adjust:inherit;font-kerning:inherit;font-feature-settings:inherit;font-variation-settings:inherit;font-language-override:inherit;margin:0;padding:0;vertical-align:baseline;color:rgb(24,32,38);font-size:14px;" segoe="segoe" ui="ui" sans="sans" neue="neue">{text}</span></p>'


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


def create_draft(token, article_data):
    """创建微信公众号草稿"""
    url = f"{WECHAT_API_BASE}/draft/add?access_token={token}"
    payload = {"articles": [article_data]}
    
    print(f"[INFO] 正在创建草稿：{article_data.get('title', '')}")
    response = requests.post(url, data=json.dumps(payload, ensure_ascii=False).encode('utf-8'), 
                             headers={'Content-Type': 'application/json; charset=utf-8'}, timeout=60)
    result = response.json()
    
    if result.get('errcode', 0) != 0:
        raise Exception(f"创建草稿失败：{result}")
    
    print("[OK] 草稿创建成功")
    return result


def convert_article(paragraphs, article_meta, chinese_translations=None, cover_image_html=None):
    """
    转换文章为微信公众号格式
    
    Args:
        paragraphs: 段落列表
        article_meta: 文章元数据
        chinese_translations: 中文翻译列表
        cover_image_html: 封面图 HTML（如果提供会在副标题后插入）
    
    Returns:
        转换后的 HTML 字符串
    """
    html_parts = []
    
    # 副标题（英文）
    if article_meta.get('subtitle_en'):
        html_parts.append(f'<h1 style="border:0;font-style:normal;font-variant:oldstyle-nums;font-weight:400;font-stretch:inherit;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;margin:0;padding:0;color:rgb(13,13,13);text-align:start;"><span leaf="">{article_meta["subtitle_en"]}</span></h1>')
    
    # 副标题（中文）
    if article_meta.get('subtitle_zh'):
        html_parts.append(format_chinese_paragraph(article_meta['subtitle_zh']))
    
    # 封面图（如果提供）- 在副标题中文之后
    if cover_image_html:
        html_parts.append(cover_image_html)
    
    # 处理正文段落
    for i, para in enumerate(paragraphs):
        inner_html = para['innerHTML']
        has_initial = para.get('has_initial', False)
        
        if has_initial:
            # 第一段 - 带首字母大写
            html_parts.append(format_first_paragraph(inner_html))
            print(f"[INFO] 段落 {i+1}: 使用首字母大写格式")
        else:
            # 普通段落 - 转换原文的 small 标签
            html_parts.append(format_paragraph(inner_html))
            print(f"[INFO] 段落 {i+1}: 普通格式（转换原文 small 标签）")
        
        # 添加中文翻译
        if chinese_translations and i < len(chinese_translations):
            html_parts.append(format_chinese_paragraph(chinese_translations[i]))
    
    # 隐藏样式标签
    html_parts.append('<p style="display:none;"><mp-style-type data-value="10000"></mp-style-type></p>')
    
    return ''.join(html_parts)


def test_small_conversion():
    """测试 small 标签转换功能"""
    print("=" * 60)
    print("测试 small 标签转换功能")
    print("=" * 60)
    
    test_cases = [
        '<small>AI</small> research is advancing rapidly.',
        'The <small>IPO</small> was successful.',
        '<small>SEC</small> announced new regulations.',
        '<small>S</small>&amp;<small>P</small> 500 reached a new high.',
        'She studied at <small>MIT</small>.',
        'The <small>CEO</small> announced earnings.',
    ]
    
    for inner_html in test_cases:
        result = convert_small_tags(inner_html)
        print(f"\n原文：{inner_html}")
        print(f"转换：{result}")
    
    print("\n" + "=" * 60)


def main():
    """主函数 - 示例用法"""
    print("=" * 60)
    print("经济学人文章转换为微信公众号格式")
    print("=" * 60)
    
    # 测试 small 标签转换
    test_small_conversion()
    
    # 示例：转换 IPO 文章
    print("\n[示例] 转换 IPO 文章...")
    
    # 从浏览器抓取的段落（innerHTML，包含原文的 small 标签）
    paragraphs = [
        {'innerHTML': "America's regulators and market operators are teaming up to rekindle public listings", 'has_initial': False},
        {'innerHTML': '<span data-caps="initial">A</span><small>nybody who</small> has "not been through a public-company experience may think that being public is desirable. This is not so," wrote Elon Musk in a message to employees of SpaceX, his rocket company, in 2013, adding that it might not list "until Mars is secure". Since then the world\'s richest man seems to have softened his stance: SpaceX, which recently merged with x<small>AI</small>, Mr Musk\'s artificial-intelligence lab, is this year expected to list its shares in the largest initial public offering (<small>IPO</small>) of all time. The $75bn Mr Musk is reportedly seeking to raise, at a value for the company of $1.75trn, would be twice as much as the next-largest offering, of shares in Saudi Aramco in 2019.', 'has_initial': True},
        {'innerHTML': 'SpaceX may not be this year\'s only mega-<small>IPO; </small>Open<small>AI</small> and Anthropic, leading model-makers, are also said to be eyeing a listing. That will hearten those who have complained about the growing aversion of American companies to public markets. The number of listed American businesses has fallen by more than a third since the mid-1990s as the cost of compliance has risen and private markets have expanded and matured. Buy-out barons have gobbled up many public companies, while startups have increasingly opted to remain in the hands of venture backers or else sell themselves to larger incumbents. Now, however, regulators and the companies that keep public markets running want to make <small>IPO</small>s great again.', 'has_initial': False},
    ]
    
    # 文章元数据
    article_meta = {
        'title_zh': "让 IPO 再次伟大的计划",
        'title_en': "The plan to make IPOs great again",
        'subtitle_zh': "美国监管者和市场运营商正携手重振上市公司",
        'subtitle_en': "America's regulators and market operators are teaming up to rekindle public listings",
        'author': "The Economist",
        'digest': "SpaceX 预计进行史上最大 IPO，募资 750 亿美元",
        'source_url': "https://www.economist.com/business/2026/03/29/the-plan-to-make-ipos-great-again"
    }
    
    # 中文翻译（示例）
    chinese_translations = [
        "美国监管者和市场运营商正携手重振上市公司",
        "\"任何没有经历过上市公司体验的人可能认为上市是可取的。事实并非如此，\"埃隆·马斯克在 2013 年发给 SpaceX 员工的消息中写道...",
        "SpaceX 可能不是今年唯一的巨型 IPO；OpenAI 和 Anthropic 等领先的模型制造商也被认为在考虑上市...",
    ]
    
    # 转换文章
    content_html = convert_article(paragraphs, article_meta, chinese_translations)
    
    # 保存 HTML 到文件
    output_file = TEMP_DIR / 'ipo_article_demo.html'
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('<!DOCTYPE html>\n')
        f.write('<html>\n')
        f.write('<head>\n')
        f.write('  <meta charset="UTF-8">\n')
        f.write('  <title>经济学人 - 让 IPO 再次伟大的计划</title>\n')
        f.write('</head>\n')
        f.write('<body>\n')
        f.write(content_html)
        f.write('\n</body>\n')
        f.write('</html>\n')
    
    print(f"\n[OK] HTML 已保存到：{output_file}")
    print(f"[INFO] 文件大小：{output_file.stat().st_size} bytes")
    
    print("\n" + "=" * 60)
    print("转换完成！")
    print("=" * 60)


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
