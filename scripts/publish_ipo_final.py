# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
发布 IPO 文章到微信公众号
文章：The plan to make IPOs great again
"""

import sys
sys.path.insert(0, 'scripts')

from economist_to_wechat import convert_article, get_access_token, create_draft
import json
from pathlib import Path

# 配置
WORKSPACE = Path.home() / '.openclaw' / 'workspace'
TEMP_DIR = WORKSPACE / 'temp' / 'wechat_images'

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

# 从浏览器抓取的段落（innerHTML，包含原文的 small 标签）
PARAGRAPHS = [
    # 副标题
    {'innerHTML': "America's regulators and market operators are teaming up to rekindle public listings", 'has_initial': False},
    
    # 第 1 段（带首字母）
    {'innerHTML': '<span data-caps="initial">A</span><small>nybody who</small> has "not been through a public-company experience may think that being public is desirable. This is not so," wrote Elon Musk in a message to employees of SpaceX, his rocket company, in 2013, adding that it might not list "until Mars is secure". Since then the world\'s richest man seems to have softened his stance: SpaceX, which recently merged with x<small>AI</small>, Mr Musk\'s artificial-intelligence lab, is this year expected to list its shares in the largest initial public offering (<small>IPO</small>) of all time. The $75bn Mr Musk is reportedly seeking to raise, at a value for the company of $1.75trn, would be twice as much as the next-largest offering, of shares in Saudi Aramco in 2019.', 'has_initial': True},
    
    # 第 2 段
    {'innerHTML': 'SpaceX may not be this year\'s only mega-<small>IPO; </small>Open<small>AI</small> and Anthropic, leading model-makers, are also said to be eyeing a listing. That will hearten those who have complained about the growing aversion of American companies to public markets. The number of listed American businesses has fallen by more than a third since the mid-1990s as the cost of compliance has risen and private markets have expanded and matured. Buy-out barons have gobbled up many public companies, while startups have increasingly opted to remain in the hands of venture backers or else sell themselves to larger incumbents. Now, however, regulators and the companies that keep public markets running want to make <small>IPO</small>s great again.', 'has_initial': False},
    
    # 第 3 段
    {'innerHTML': 'In December Paul Atkins, Donald Trump\'s appointee as chair of the Securities and Exchange Commission, lamented that the diminution of public markets had "eroded American competitiveness, locked average investors out of some of the most dynamic companies and pushed entrepreneurs to seek capital elsewhere". He is pursuing several solutions, with a focus on reducing the regulatory burden of being a public company. The <small>SEC</small> is currently drafting a proposal to allow listed firms to file reports twice a year rather than quarterly, a change Mr Trump has endorsed. It is also looking to reduce disclosure mandates, including those relating to companies\' climate impact. And it wants to curb the power that proxy advisers, passive funds and class-action litigants have over bosses.', 'has_initial': False},
    
    # 第 4 段
    {'innerHTML': 'Compilers of stock indices are also joining in the effort to revive interest in listings. They care because companies\' reluctance to go public undermines one of their main selling points: that their indices include the most important firms in the economy. According to <small>S</small>&amp;<small>P</small> Global, which manages the <small>S</small>&amp;<small>P</small> 500 and Dow Jones indices, the collective value of the ten largest venture-backed companies has increased 1,500% over the past five years, to nearly $3trn. It and its competitors yearn to add these companies to their rolls.', 'has_initial': False},
    
    # 第 5 段
    {'innerHTML': 'One proposal is to reduce the time businesses must wait after an <small>IPO</small> before they can be included in an index, known as the "seasoning" period, which at present usually ranges from three months to a year. That would bring forward billions of dollars\' worth of stock purchases by passive funds. Nasdaq has suggested a "fast-entry" period of 15 trading days for suspiciously SpaceX-shaped companies seeking admission to its <small>Nasdaq</small> 100 index; <small>LSEG</small> has suggested five trading days for entry to its Russell indices. Another carrot they are considering is reducing the percentage of shares companies must float before being eligible for index inclusion. <small>S</small>&amp;<small>P</small> Global is reportedly weighing similar changes.', 'has_initial': False},
    
    # 第 6 段
    {'innerHTML': 'For Nasdaq, encouraging more companies to go public would be doubly sweet, since it also runs a stock exchange that rakes in fees when firms list (and annually thereafter). It is competing with the New York Stock Exchange to win the SpaceX listing, and Mr Musk has reportedly made early index inclusion a condition of winning his favour.', 'has_initial': False},
    
    # 第 7 段
    {'innerHTML': 'The three mega-<small>IPO</small>s will also gladden those who want to see the wealth generated by <small>AI</small> spread more widely. Still, there may be losers from the changes. Consider the impact on passive funds. One purpose of the seasoning period is to allow the market to settle on a price for a firm\'s shares before these investors must buy them; reducing that period may force them to buy overpriced shares. The problem may be compounded by the change to the free-float rules, which would mechanically raise demand from passive funds while keeping the supply of shares constrained, pushing up the price. Since 1980 all but one of the large firms that initially floated less than 5% of their stock underperformed the market over the next three years, according to data compiled by Jay Ritter of the University of Florida. Retail traders may also struggle to get their hands on the shares of the hottest companies.', 'has_initial': False},
    
    # 第 8 段（带结束符号）
    {'innerHTML': 'The coming months, then, will serve as a test of the balance of power between public markets and private companies. At present the latter seem to have the upper hand. Index operators in particular are "anxious to please without regard to potential consequences", says Patrick Healy, who has negotiated <small>IPO</small> terms with them for many big companies. Still, there are limits to the sway held by bosses such as Mr Musk, who need the vast pools of money available in public markets to fund their ambitions. After all, getting to Mars is not cheap. <span class="ufinish">■</span>', 'has_initial': False},
]

# 中文翻译（简化版，用于测试）
CHINESE_TRANSLATIONS = [
    "美国监管者和市场运营商正携手重振上市公司",
    "\"任何没有经历过上市公司体验的人可能认为上市是可取的。事实并非如此，\"埃隆·马斯克在 2013 年发给 SpaceX 员工的消息中写道...",
    "SpaceX 可能不是今年唯一的巨型 IPO；OpenAI 和 Anthropic 等领先的模型制造商也被认为在考虑上市...",
    "12 月，特朗普任命的 SEC 主席保罗·阿特金斯 lamented 公开市场的减少...",
    "股票指数编制者也加入了重振上市兴趣的努力...",
    "一项提议是缩短企业 IPO 后必须等待才能被纳入指数的时间...",
    "对纳斯达克来说，鼓励更多公司上市将是双重甜蜜...",
    "这三项巨型 IPO 也将让那些希望看到 AI 产生的财富更广泛传播的人感到高兴...",
    "因此，未来几个月将作为公开市场和私营公司之间权力平衡的考验... ■",
]


def main():
    print("=" * 60)
    print("发布 IPO 文章到微信公众号")
    print("=" * 60)
    
    # 获取 token
    print("\n[INFO] 获取 access_token...")
    token = get_access_token()
    print(f"[OK] 获取 access_token 成功")
    
    # 转换文章
    print("\n[INFO] 转换文章内容...")
    content_html = convert_article(PARAGRAPHS, ARTICLE_META, CHINESE_TRANSLATIONS)
    
    # 保存 HTML 到文件
    output_file = TEMP_DIR / 'ipo_article_wechat.html'
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
    
    print(f"[OK] HTML 已保存到：{output_file}")
    print(f"[INFO] 文件大小：{output_file.stat().st_size} bytes")
    
    # 创建标题
    MAX_TITLE_LEN = 60
    full_title = f'经济学人 | {ARTICLE_META["title_zh"]} | {ARTICLE_META["title_en"]}'
    
    if len(full_title) > MAX_TITLE_LEN:
        full_title = f'{ARTICLE_META["title_zh"]} | {ARTICLE_META["title_en"]}'
    
    # 创建草稿
    article_data = {
        'title': full_title,
        'author': ARTICLE_META['author'],
        'digest': ARTICLE_META['digest'],
        'content': content_html,
        'content_source_url': ARTICLE_META['source_url']
    }
    
    print("\n[INFO] 创建微信公众号草稿...")
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
