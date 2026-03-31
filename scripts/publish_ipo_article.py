# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
发布 IPO 文章到微信公众号
"""

import json
import re
import time
import requests
from pathlib import Path

# 配置
WORKSPACE = Path.home() / '.openclaw' / 'workspace'
CREDENTIALS_FILE = WORKSPACE / '.wechat-credentials.json'
TOKEN_CACHE_FILE = WORKSPACE / '.wechat-token-cache.json'
TEMP_DIR = WORKSPACE / 'temp' / 'wechat_images'
WECHAT_API_BASE = "https://api.weixin.qq.com/cgi-bin"

# 完整的 <small> 标签样式
SMALL_STYLE = 'border:0;font-style:inherit;font-variant-ligatures:none;font-variant-caps:small-caps;font-variant-numeric:normal;font-variant-east-asian:normal;font-variant-alternates:normal;font-variant-position:normal;font-variant-emoji:normal;font-weight:inherit;font-stretch:inherit;line-height:inherit;font-family:inherit;font-size:inherit;margin:0;padding:0;vertical-align:baseline;display:inline;text-transform:lowercase;'

# 文章元数据
ARTICLE_META = {
    'title_zh': "让 IPO 再次伟大的计划",
    'title_en': "The plan to make IPOs great again",
    'subtitle_zh': "美国监管者和市场运营商正携手重振上市公司",
    'subtitle_en': "America's regulators and market operators are teaming up to rekindle public listings",
    'author': "The Economist",
    'digest': "SpaceX 预计进行史上最大 IPO，募资 750 亿美元，OpenAI 等 AI 公司也在考虑上市",
    'source_url': "https://www.economist.com/business/2026/03/29/the-plan-to-make-ipos-great-again"
}

# 从浏览器抓取的原文段落（包含 innerHTML）
ORIGINAL_PARAGRAPHS = [
    # 副标题
    {
        'has_initial': False,
        'innerHTML': "America's regulators and market operators are teaming up to rekindle public listings"
    },
    # 第 1 段（带首字母）
    {
        'has_initial': True,
        'innerHTML': """<span data-caps="initial">A</span><small>nybody who</small> has "not been through a public-company experience may think that being public is desirable. This is not so," wrote Elon Musk in a message to employees of SpaceX, his rocket company, in 2013, adding that it might not list "until Mars is secure". Since then the world's richest man seems to have softened his stance: SpaceX, which recently merged with x<small>AI</small>, Mr Musk's artificial-intelligence lab, is this year expected to list its shares in the largest initial public offering (<small>IPO</small>) of all time. The $75bn Mr Musk is reportedly seeking to raise, at a value for the company of $1.75trn, would be twice as much as the next-largest offering, of shares in Saudi Aramco in 2019."""
    },
    # 第 2 段
    {
        'has_initial': False,
        'innerHTML': """SpaceX may not be this year's only mega-<small>IPO; </small>Open<small>AI</small> and Anthropic, leading model-makers, are also said to be eyeing a listing. That will hearten those who have complained about the growing aversion of American companies to public markets. The number of listed American businesses has fallen by more than a third since the mid-1990s as the cost of compliance has risen and private markets have expanded and matured (see chart). Buy-out barons have gobbled up many public companies, while startups have increasingly opted to remain in the hands of venture backers or else sell themselves to larger incumbents. Now, however, regulators and the companies that keep public markets running want to make <small>IPO</small>s great again."""
    },
    # 第 3 段
    {
        'has_initial': False,
        'innerHTML': """In December Paul Atkins, Donald Trump's appointee as chair of the Securities and Exchange Commission, lamented that the diminution of public markets had "eroded American competitiveness, locked average investors out of some of the most dynamic companies and pushed entrepreneurs to seek capital elsewhere". He is pursuing several solutions, with a focus on reducing the regulatory burden of being a public company. The <small>SEC</small> is currently drafting a proposal to allow listed firms to file reports twice a year rather than quarterly, a change Mr Trump has endorsed. It is also looking to reduce disclosure mandates, including those relating to companies' climate impact. And it wants to curb the power that proxy advisers, passive funds and class-action litigants have over bosses."""
    },
    # 第 4 段
    {
        'has_initial': False,
        'innerHTML': """Compilers of stock indices are also joining in the effort to revive interest in listings. They care because companies' reluctance to go public undermines one of their main selling points: that their indices include the most important firms in the economy. According to <small>S</small>&amp;<small>P</small> Global, which manages the <small>S</small>&amp;<small>P</small> 500 and Dow Jones indices, the collective value of the ten largest venture-backed companies has increased 1,500% over the past five years, to nearly $3trn. It and its competitors yearn to add these companies to their rolls."""
    },
    # 第 5 段
    {
        'has_initial': False,
        'innerHTML': """One proposal is to reduce the time businesses must wait after an <small>IPO</small> before they can be included in an index, known as the "seasoning" period, which at present usually ranges from three months to a year. That would bring forward billions of dollars' worth of stock purchases by passive funds. Nasdaq has suggested a "fast-entry" period of 15 trading days for suspiciously SpaceX-shaped companies seeking admission to its <small>Nasdaq</small> 100 index; <small>LSEG</small> has suggested five trading days for entry to its Russell indices. Another carrot they are considering is reducing the percentage of shares companies must float before being eligible for index inclusion. <small>S</small>&amp;<small>P</small> Global is reportedly weighing similar changes."""
    },
    # 第 6 段
    {
        'has_initial': False,
        'innerHTML': """For Nasdaq, encouraging more companies to go public would be doubly sweet, since it also runs a stock exchange that rakes in fees when firms list (and annually thereafter). It is competing with the New York Stock Exchange to win the SpaceX listing, and Mr Musk has reportedly made early index inclusion a condition of winning his favour."""
    },
    # 第 7 段
    {
        'has_initial': False,
        'innerHTML': """The three mega-<small>IPO</small>s will also gladden those who want to see the wealth generated by <small>AI</small> spread more widely. Still, there may be losers from the changes. Consider the impact on passive funds. One purpose of the seasoning period is to allow the market to settle on a price for a firm's shares before these investors must buy them; reducing that period may force them to buy overpriced shares. The problem may be compounded by the change to the free-float rules, which would mechanically raise demand from passive funds while keeping the supply of shares constrained, pushing up the price. Since 1980 all but one of the large firms that initially floated less than 5% of their stock underperformed the market over the next three years, according to data compiled by Jay Ritter of the University of Florida. Retail traders may also struggle to get their hands on the shares of the hottest companies."""
    },
    # 第 8 段（带结束符号）
    {
        'has_initial': False,
        'innerHTML': """The coming months, then, will serve as a test of the balance of power between public markets and private companies. At present the latter seem to have the upper hand. Index operators in particular are "anxious to please without regard to potential consequences", says Patrick Healy, who has negotiated <small>IPO</small> terms with them for many big companies. Still, there are limits to the sway held by bosses such as Mr Musk, who need the vast pools of money available in public markets to fund their ambitions. After all, getting to Mars is not cheap. <span class="ufinish">■</span>"""
    }
]


def convert_inner_html_to_wechat(inner_html):
    """将原文的 innerHTML 转换为微信公众号格式"""
    # 移除 <i> 标签
    html = inner_html.replace('<i>', '').replace('</i>', '')
    
    # 替换 &amp; 为 &
    html = html.replace('&amp;', '&')
    
    # 替换 <small> 标签为带样式的 small 标签
    def replace_small(match):
        content = match.group(1)
        return f'<small style="{SMALL_STYLE}">{content}</small>'
    
    html = re.sub(r'<small>(.*?)</small>', replace_small, html)
    
    # 替换结束符号
    html = html.replace('<span class="ufinish">■</span>', '<span style="color:rgb(227,18,11)">■</span>')
    
    return html


def format_first_paragraph(inner_html):
    """格式化第一段（带首字母大写）"""
    html = convert_inner_html_to_wechat(inner_html)
    
    # 替换 initial span 的样式
    html = html.replace(
        '<span data-caps="initial">',
        '<span style="font-size:3.5rem;float:left;height:3.25rem;text-transform:uppercase;margin:0 0.2rem 0 0;">'
    )
    
    return f'<section style="margin:0;padding:0;text-align:start;"><p style="margin:0;padding:0;font-size:20px;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;color:rgb(13,13,13);">{html}</p></section>'


def format_paragraph(inner_html):
    """格式化普通段落"""
    html = convert_inner_html_to_wechat(inner_html)
    
    return f'<section style="margin:0.875rem 0 0;padding:0;text-align:start;"><p style="margin:0;padding:0;font-size:20px;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;color:rgb(13,13,13);">{html}</p></section>'


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


def create_draft(token, article_data):
    url = f"{WECHAT_API_BASE}/draft/add?access_token={token}"
    payload = {"articles": [article_data]}
    
    print(f"[INFO] 正在创建草稿：{article_data.get('title', '')}")
    print(f"[INFO] 内容长度：{len(article_data.get('content', ''))} 字符")
    response = requests.post(url, data=json.dumps(payload, ensure_ascii=False).encode('utf-8'), 
                             headers={'Content-Type': 'application/json; charset=utf-8'}, timeout=60)
    result = response.json()
    
    print(f"[DEBUG] API 返回：{result}")
    
    if result.get('errcode', 0) != 0:
        raise Exception(f"创建草稿失败：{result}")
    
    print("[OK] 草稿创建成功")
    return result


def main():
    print("=" * 60)
    print("发布经济学人文章到微信公众号")
    print("=" * 60)
    
    # 获取 token
    token = get_access_token()
    print(f"[OK] 获取 access_token 成功")
    
    # 构建 HTML
    print("\n[INFO] 构建文章内容...")
    html_parts = []
    
    # 副标题（英文）
    html_parts.append(f'<section style="margin:0;padding:0;text-align:start;"><h1 style="margin:0;padding:0;font-size:20px;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;color:rgb(13,13,13);">{ORIGINAL_PARAGRAPHS[0]["innerHTML"]}</h1></section>')
    
    # 副标题（中文）
    html_parts.append(f'<section style="margin:0 0 8px;padding:0;text-align:start;"><p style="margin:0;padding:0;font-size:14px;line-height:28px;font-family:sans-serif;color:rgb(24,32,38);">美国监管者和市场运营商正携手重振上市公司</p></section>')
    
    # 处理正文段落（从 index 1 开始）
    for i, para in enumerate(ORIGINAL_PARAGRAPHS[1:], start=1):
        if para['has_initial']:
            html_parts.append(format_first_paragraph(para['innerHTML']))
            print(f"[INFO] 段落 {i}: 使用首字母大写格式")
        else:
            html_parts.append(format_paragraph(para['innerHTML']))
            print(f"[INFO] 段落 {i}: 普通格式")
        
        # 添加中文翻译占位
        html_parts.append(f'<section style="margin:8px 0 16px;padding:0;text-align:start;"><p style="margin:0;padding:0;font-size:14px;line-height:28px;font-family:sans-serif;color:rgb(24,32,38);">[中文翻译待添加]</p></section>')
    
    content_html = ''.join(html_parts)
    
    # 保存 HTML 到文件检查
    output_file = TEMP_DIR / 'ipo_article_test.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Test</title></head><body>')
        f.write(content_html)
        f.write('</body></html>')
    print(f"[INFO] HTML 已保存到：{output_file}")
    
    # 创建草稿
    MAX_TITLE_LEN = 60
    full_title = f'经济学人 | {ARTICLE_META["title_zh"]} | {ARTICLE_META["title_en"]}'
    
    if len(full_title) > MAX_TITLE_LEN:
        full_title = f'{ARTICLE_META["title_zh"]} | {ARTICLE_META["title_en"]}'
    
    article_data = {
        'title': full_title,
        'author': ARTICLE_META['author'],
        'digest': ARTICLE_META['digest'],
        'content': content_html,
        'content_source_url': ARTICLE_META['source_url']
    }
    
    draft_result = create_draft(token, article_data)
    draft_media_id = draft_result.get('media_id')
    
    print("\n" + "=" * 60)
    print("[OK] 发布完成！")
    print("=" * 60)
    print(f"[TITLE] {full_title}")
    print(f"[DIGEST] {ARTICLE_META['digest']}")
    print(f"\n[DRAFT_ID] {draft_media_id}")
    print(f"\n[URL] https://mp.weixin.qq.com")
    print("=" * 60)
    
    return draft_media_id


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
