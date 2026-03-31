# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
发布 IPO 文章到微信公众号（完整版）
包含：导读 + 正文 + 英语学习讲解
"""

import sys
sys.path.insert(0, 'scripts')

from economist_to_wechat import convert_article, get_access_token, create_draft, WECHAT_API_BASE
import requests
import json
from pathlib import Path

# 配置
WORKSPACE = Path.home() / '.openclaw' / 'workspace'
TEMP_DIR = WORKSPACE / 'temp' / 'wechat_images'

# 封面图 URL
COVER_IMAGE_URL = "https://www.economist.com/cdn-cgi/image/width=1424,quality=80,format=auto/content-assets/images/20260328_WBP504.jpg"

# 文章元数据
ARTICLE_META = {
    'title_zh': "让 IPO 再次伟大的计划",
    'title_en': "The plan to make IPOs great again",
    'subtitle_zh': "美国监管者和市场运营商正携手重振上市公司",
    'subtitle_en': "America's regulators and market operators are teaming up to rekindle public listings",
    'author': "The Economist",
    'digest': "SpaceX 预计进行史上最大 IPO，募资 750 亿美元，OpenAI 等 AI 公司也在考虑上市",
    'source_url': "https://www.economist.com/business/2026/03/29/the-plan-to-make-ipos-great-again",
    'cover_image_url': COVER_IMAGE_URL
}

# 从浏览器抓取的段落（innerHTML，包含原文的 small 标签）
PARAGRAPHS = [
    {'innerHTML': '<span data-caps="initial">A</span><small>nybody who</small> has "not been through a public-company experience may think that being public is desirable. This is not so," wrote Elon Musk in a message to employees of SpaceX, his rocket company, in 2013, adding that it might not list "until Mars is secure". Since then the world\'s richest man seems to have softened his stance: SpaceX, which recently merged with xAI, Mr Musk\'s artificial-intelligence lab, is this year expected to list its shares in the largest initial public offering (IPO) of all time. The $75bn Mr Musk is reportedly seeking to raise, at a value for the company of $1.75trn, would be twice as much as the next-largest offering, of shares in Saudi Aramco in 2019.', 'has_initial': True},
    {'innerHTML': 'SpaceX may not be this year\'s only mega-<small>IPO; </small>Open<small>AI</small> and Anthropic, leading model-makers, are also said to be eyeing a listing. That will hearten those who have complained about the growing aversion of American companies to public markets. The number of listed American businesses has fallen by more than a third since the mid-1990s as the cost of compliance has risen and private markets have expanded and matured. Buy-out barons have gobbled up many public companies, while startups have increasingly opted to remain in the hands of venture backers or else sell themselves to larger incumbents. Now, however, regulators and the companies that keep public markets running want to make <small>IPO</small>s great again.', 'has_initial': False},
    {'innerHTML': 'In December Paul Atkins, Donald Trump\'s appointee as chair of the Securities and Exchange Commission, lamented that the diminution of public markets had "eroded American competitiveness, locked average investors out of some of the most dynamic companies and pushed entrepreneurs to seek capital elsewhere". He is pursuing several solutions, with a focus on reducing the regulatory burden of being a public company. The <small>SEC</small> is currently drafting a proposal to allow listed firms to file reports twice a year rather than quarterly, a change Mr Trump has endorsed. It is also looking to reduce disclosure mandates, including those relating to companies\' climate impact. And it wants to curb the power that proxy advisers, passive funds and class-action litigants have over bosses.', 'has_initial': False},
    {'innerHTML': 'Compilers of stock indices are also joining in the effort to revive interest in listings. They care because companies\' reluctance to go public undermines one of their main selling points: that their indices include the most important firms in the economy. According to <small>S</small>&amp;<small>P</small> Global, which manages the <small>S</small>&amp;<small>P</small> 500 and Dow Jones indices, the collective value of the ten largest venture-backed companies has increased 1,500% over the past five years, to nearly $3trn. It and its competitors yearn to add these companies to their rolls.', 'has_initial': False},
    {'innerHTML': 'One proposal is to reduce the time businesses must wait after an <small>IPO</small> before they can be included in an index, known as the "seasoning" period, which at present usually ranges from three months to a year. That would bring forward billions of dollars\' worth of stock purchases by passive funds. Nasdaq has suggested a "fast-entry" period of 15 trading days for suspiciously SpaceX-shaped companies seeking admission to its <small>Nasdaq</small> 100 index; <small>LSEG</small> has suggested five trading days for entry to its Russell indices. Another carrot they are considering is reducing the percentage of shares companies must float before being eligible for index inclusion. <small>S</small>&amp;<small>P</small> Global is reportedly weighing similar changes.', 'has_initial': False},
    {'innerHTML': 'For Nasdaq, encouraging more companies to go public would be doubly sweet, since it also runs a stock exchange that rakes in fees when firms list (and annually thereafter). It is competing with the New York Stock Exchange to win the SpaceX listing, and Mr Musk has reportedly made early index inclusion a condition of winning his favour.', 'has_initial': False},
    {'innerHTML': 'The three mega-<small>IPO</small>s will also gladden those who want to see the wealth generated by <small>AI</small> spread more widely. Still, there may be losers from the changes. Consider the impact on passive funds. One purpose of the seasoning period is to allow the market to settle on a price for a firm\'s shares before these investors must buy them; reducing that period may force them to buy overpriced shares. The problem may be compounded by the change to the free-float rules, which would mechanically raise demand from passive funds while keeping the supply of shares constrained, pushing up the price. Since 1980 all but one of the large firms that initially floated less than 5% of their stock underperformed the market over the next three years, according to data compiled by Jay Ritter of the University of Florida. Retail traders may also struggle to get their hands on the shares of the hottest companies.', 'has_initial': False},
    {'innerHTML': 'The coming months, then, will serve as a test of the balance of power between public markets and private companies. At present the latter seem to have the upper hand. Index operators in particular are "anxious to please without regard to potential consequences", says Patrick Healy, who has negotiated <small>IPO</small> terms with them for many big companies. Still, there are limits to the sway held by bosses such as Mr Musk, who need the vast pools of money available in public markets to fund their ambitions. After all, getting to Mars is not cheap. <span class="ufinish">■</span>', 'has_initial': False},
]

# 中文翻译（完整版）
CHINESE_TRANSLATIONS = [
    "\"任何没有经历过上市公司体验的人可能认为上市是可取的。事实并非如此，\"埃隆·马斯克在 2013 年发给 SpaceX 员工的消息中写道，并补充说该公司可能不会上市，\"直到火星安全为止\"。此后，这位世界首富似乎软化了他的立场：SpaceX 最近与马斯克的 AI 实验室 xAI 合并，预计今年将进行史上最大规模的首次公开募股（IPO）。据报道，马斯克寻求募资 750 亿美元，公司估值达 1.75 万亿美元，是 2019 年沙特阿美 IPO 的两倍。",
    "SpaceX 可能不是今年唯一的巨型 IPO；OpenAI 和 Anthropic 等领先的模型制造商也被认为在考虑上市。这将鼓舞那些一直抱怨美国公司越来越厌恶公开市场的人。自 1990 年代中期以来，随着合规成本上升和私募市场扩大成熟，美国上市公司数量减少了超过三分之一。收购巨头吞并了许多上市公司，而初创公司越来越选择留在风险投资支持者手中，或将自己出售给更大的现有企业。然而，现在监管者和维持公开市场运营的公司想让 IPO 再次伟大。",
    "12 月，唐纳德·特朗普任命的美国证券交易委员会（SEC）主席保罗·阿特金斯 lamented 公开市场的减少\"侵蚀了美国竞争力，将普通投资者拒于一些最具活力的公司之外，并迫使企业家到别处寻求资本\"。他正在寻求多种解决方案，重点是减轻上市公司的监管负担。SEC 目前正在起草一项提案，允许上市公司每年提交两次报告而不是每季度一次，特朗普已认可这一变化。SEC 还希望减少披露要求，包括与公司气候影响相关的披露。它还希望遏制代理顾问、被动基金和集体诉讼诉讼人对老板的权力。",
    "股票指数编制者也加入了重振上市兴趣的努力。他们关心是因为公司不愿上市削弱了他们的主要卖点之一：他们的指数包含经济中最重要的公司。根据管理标普 500 和道琼斯指数的标普全球公司，十大风险支持公司的集体价值在过去五年中增长了 1500%，达到近 3 万亿美元。它及其竞争对手渴望将这些公司添加到他们的名单中。",
    "一项提议是缩短企业 IPO 后必须等待才能被纳入指数的时间，称为\"成熟期\"，目前通常为三个月到一年。这将提前被动基金数十亿美元的股票购买。纳斯达克已建议为寻求纳入纳斯达克 100 指数的 SpaceX 形状公司提供 15 个交易日的\"快速进入\"期；伦敦证券交易所集团（LSEG）已建议进入其罗素指数的等待期为五个交易日。他们考虑的另一个激励措施是降低公司必须有资格纳入指数前必须流通的股份百分比。据报道，标普全球正在权衡类似的变化。",
    "对纳斯达克来说，鼓励更多公司上市将是双重甜蜜，因为它还运营着一个证券交易所，在公司上市时（以及之后每年）收取费用。它正在与纽约证券交易所竞争赢得 SpaceX 上市，据报道马斯克已将早期纳入指数作为赢得他青睐的条件。",
    "这三项巨型 IPO 也将让那些希望看到 AI 产生的财富更广泛传播的人感到高兴。然而，这些变化可能会有输家。考虑对被动基金的影响。成熟期的一个目的是让这些投资者必须购买公司股票之前，让市场确定公司股票的价格；缩短这一期限可能迫使他们购买定价过高的股票。自由流通规则的变化可能会加剧这个问题，这将机械地提高被动基金的需求，同时保持股票供应受限，推高价格。根据佛罗里达大学 Jay Ritter 编制的数据，自 1980 年以来，几乎所有最初流通股份低于 5% 的大型公司在接下来三年内都跑输了市场。散户交易者也可能难以获得最热门公司的股票。",
    "因此，未来几个月将作为公开市场和私营公司之间权力平衡的考验。目前后者似乎占据上风。特别是指数运营商\"急于取悦而不顾潜在后果\"，帕特里克·希利说，他曾为许多大公司与他们谈判 IPO 条款。然而，像马斯克这样的老板的影响力是有限度的，他们需要公开市场上的巨额资金来资助他们的雄心。毕竟，去火星并不便宜。■",
]

# 导读部分
READING_GUIDE = """
<section style="margin:20px 0;padding:20px;background-color:rgb(245,248,250);border-left:4px solid rgb(0,100,0);border-radius:5px;">
  <h2 style="font-size:18px;margin:0 0 15px;padding:0;color:rgb(13,13,13);">📖 Reading Guide | 导读</h2>
  
  <h3 style="font-size:16px;margin:20px 0 10px;padding:0;color:rgb(0,100,0);">🔑 Key Points | 文章要点</h3>
  <ul style="margin:0 0 0 20px;padding:0;color:rgb(13,13,13);font-size:15px;line-height:2;">
    <li style="margin-bottom:8px;">SpaceX 预计进行史上最大 IPO，募资 750 亿美元，估值达 1.75 万亿美元</li>
    <li style="margin-bottom:8px;">OpenAI 和 Anthropic 等 AI 公司也在考虑上市</li>
    <li style="margin-bottom:8px;">SEC 拟将财报披露从季度改为半年度，减轻上市公司监管负担</li>
    <li style="margin-bottom:8px;">指数公司拟缩短 IPO 后纳入指数的等待期（从 3-12 个月到 5-15 天）</li>
    <li style="margin-bottom:8px;">自 1990 年代中期以来，美国上市公司数量减少超过三分之一</li>
  </ul>
  
  <h3 style="font-size:16px;margin:25px 0 10px;padding:0;color:rgb(0,100,0);">🌍 Background | 相关背景</h3>
  <p style="margin:0 0 15px;padding:0;color:rgb(13,13,13);font-size:15px;line-height:1.8;"><strong>什么是 IPO？</strong> 首次公开募股（Initial Public Offering）是指私人公司首次向公众出售股票，成为上市公司的过程。这是公司融资的重要方式，也是投资者参与公司成长的机会。</p>
  <p style="margin:0 0 15px;padding:0;color:rgb(13,13,13);font-size:15px;line-height:1.8;"><strong>为什么公司不愿上市？</strong> 随着合规成本上升（如萨班斯 - 奥克斯利法案要求），上市公司需要披露更多财务信息，接受更严格监管。同时，私募市场成熟，初创公司可以在不上市的情况下获得充足资金。</p>
  <p style="margin:0;padding:0;color:rgb(13,13,13);font-size:15px;line-height:1.8;"><strong>为什么现在要重振 IPO？</strong> 上市公司减少意味着普通投资者无法投资最具活力的公司，只能投资成熟企业。这限制了普通人的投资机会，也影响了资本市场的活力。</p>
  
  <h3 style="font-size:16px;margin:25px 0 10px;padding:0;color:rgb(0,100,0);">💡 Reading Tips | 阅读建议</h3>
  <ul style="margin:0;padding:0;color:rgb(13,13,13);font-size:15px;line-height:2;">
    <li style="margin-bottom:8px;">本文适合<strong>雅思 7.0+/托福 100+</strong>水平的学习者</li>
    <li style="margin-bottom:8px;">建议先通读全文，了解大意，再细读长难句</li>
    <li style="margin-bottom:8px;">重点关注商业/经济类词汇（IPO, compliance, incumbent 等）</li>
    <li style="margin-bottom:8px;">文章末尾有详细的词汇讲解和长难句解析</li>
  </ul>
</section>

<section style="margin:30px 0;text-align:center;">
  <div style="height:1px;background-color:rgb(200,200,200);margin:0 auto;width:80%;"></div>
</section>
"""

# 英语学习讲解分隔线
LEARNING_DIVIDER = """
<section style="margin:40px 0;text-align:center;">
  <div style="height:2px;background-color:rgb(0,100,0);margin:0 auto;width:60%;"></div>
</section>
"""

# 英语学习讲解标题
LEARNING_TITLE = """
<h1 style="border:0;font-style:normal;font-variant:oldstyle-nums;font-weight:400;font-stretch:inherit;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;margin:30px 0 16px;padding:0;color:rgb(13,13,13);text-align:start;">
  <span leaf="">📚 English Learning | 英语学习讲解</span>
</h1>
"""


def upload_temp_image(token, image_path):
    """上传临时图片到微信，返回 media_id"""
    url = f"{WECHAT_API_BASE}/media/upload?access_token={token}&type=image"
    
    print(f"[INFO] 正在上传临时图片：{image_path}")
    
    with open(image_path, 'rb') as f:
        files = {'media': f}
        response = requests.post(url, files=files, timeout=60)
    
    result = response.json()
    
    if 'media_id' in result:
        media_id = result['media_id']
        print(f"[OK] 临时图片上传成功，media_id: {media_id}")
        return media_id
    else:
        raise Exception(f"上传临时图片失败：{result}")


def upload_cover_image(token, image_path):
    """上传封面图到微信素材库（用于 thumb_media_id）"""
    url = f"{WECHAT_API_BASE}/material/add_material?access_token={token}&type=image"
    
    print(f"[INFO] 正在上传封面图：{image_path}")
    
    with open(image_path, 'rb') as f:
        files = {'media': f}
        response = requests.post(url, files=files, timeout=60)
    
    result = response.json()
    
    if result.get('errcode', 0) != 0:
        raise Exception(f"上传封面图失败：{result}")
    
    media_id = result.get('media_id')
    print(f"[OK] 封面图上传成功，media_id: {media_id}")
    
    return media_id


def main():
    print("=" * 60)
    print("发布 IPO 文章到微信公众号（完整版）")
    print("=" * 60)
    
    # 获取 token
    print("\n[INFO] 获取 access_token...")
    token = get_access_token()
    print(f"[OK] 获取 access_token 成功")
    
    # 上传封面图
    cover_path = TEMP_DIR / 'ipo_cover.jpg'
    if not cover_path.exists():
        print(f"[ERROR] 封面图不存在：{cover_path}")
        print(f"[INFO] 请先运行：python scripts/download_ipo_cover.py")
        return
    
    print("\n[INFO] 上传封面图到微信素材库...")
    thumb_media_id = upload_cover_image(token, cover_path)
    
    # 上传临时图片获取 media_id
    print("\n[INFO] 上传临时图片...")
    temp_media_id = upload_temp_image(token, cover_path)
    
    # 构建微信图片 CDN URL
    cdn_media_id = temp_media_id.replace('-', '').replace('_', '')
    cover_image_url = f"https://mmbiz.qpic.cn/mmbiz_jpg/{cdn_media_id}/0?wx_fmt=jpeg"
    
    print(f"[INFO] 图片 CDN URL: {cover_image_url}")
    
    # 构建封面图 HTML
    cover_image_html = f'<section style="text-align:center;" nodeleaf=""><img class="rich_pages wxw-img" src="{cover_image_url}" data-type="jpg" type="block"></section>'
    
    # 转换文章
    print("\n[INFO] 转换文章内容...")
    content_html = convert_article(PARAGRAPHS, ARTICLE_META, CHINESE_TRANSLATIONS, cover_image_html)
    
    # 在文章开头添加导读
    content_html = READING_GUIDE + content_html
    
    # 在文章末尾添加英语学习讲解（带分隔线）
    content_html += LEARNING_DIVIDER
    content_html += LEARNING_TITLE
    
    # 添加完整的英语学习内容
    learning_content = """
<h2 style="font-size:18px;margin:25px 0 12px;padding:0;color:rgb(13,13,13);">🔑 Key Vocabulary | 重点词汇</h2>

<p style="font-size:16px;margin:15px 0 8px;padding:0;color:rgb(13,13,13);"><strong style="color:rgb(0,100,0);">1. rekindle</strong> /ˌriːˈkɪndl/ <em>v.</em> 重新点燃，恢复</p>
<p style="font-size:14px;margin:0 0 15px 20px;padding:0;color:rgb(100,100,100);line-height:1.8;"><strong>原文：</strong>...teaming up to rekindle public listings<br><strong>释义：</strong>联手重振上市公司<br><strong>例句：</strong>The government hopes to rekindle economic growth.（政府希望重振经济增长。）</p>

<p style="font-size:16px;margin:15px 0 8px;padding:0;color:rgb(13,13,13);"><strong style="color:rgb(0,100,0);">2. aversion</strong> /əˈvɜːʃn/ <em>n.</em> 厌恶，反感</p>
<p style="font-size:14px;margin:0 0 15px 20px;padding:0;color:rgb(100,100,100);line-height:1.8;"><strong>原文：</strong>...the growing aversion of American companies to public markets<br><strong>释义：</strong>美国公司对公开市场日益增长的厌恶<br><strong>搭配：</strong>have an aversion to sth（厌恶某事）</p>

<p style="font-size:16px;margin:15px 0 8px;padding:0;color:rgb(13,13,13);"><strong style="color:rgb(0,100,0);">3. incumbent</strong> /ɪnˈkʌmbənt/ <em>n.</em> 现任者；现有企业</p>
<p style="font-size:14px;margin:0 0 15px 20px;padding:0;color:rgb(100,100,100);line-height:1.8;"><strong>原文：</strong>...sell themselves to larger incumbents<br><strong>释义：</strong>将自己出售给更大的现有企业<br><strong>商业用法：</strong>market incumbents（市场现有企业）</p>

<p style="font-size:16px;margin:15px 0 8px;padding:0;color:rgb(13,13,13);"><strong style="color:rgb(0,100,0);">4. diminish</strong> /dɪˈmɪnɪʃ/ <em>v.</em> 减少，削弱</p>
<p style="font-size:14px;margin:0 0 15px 20px;padding:0;color:rgb(100,100,100);line-height:1.8;"><strong>原文：</strong>...the diminution of public markets<br><strong>释义：</strong>公开市场的减少<br><strong>名词形式：</strong>diminution（正式用语）</p>

<p style="font-size:16px;margin:15px 0 8px;padding:0;color:rgb(13,13,13);"><strong style="color:rgb(0,100,0);">5. curb</strong> /kɜːb/ <em>v.</em> 控制，抑制</p>
<p style="font-size:14px;margin:0 0 15px 20px;padding:0;color:rgb(100,100,100);line-height:1.8;"><strong>原文：</strong>...curb the power that proxy advisers...have over bosses<br><strong>释义：</strong>遏制代理顾问对老板们的权力<br><strong>同义词：</strong>control, restrain, limit</p>

<h2 style="font-size:18px;margin:30px 0 12px;padding:0;color:rgb(13,13,13);">📖 Complex Sentences | 长难句解析</h2>

<p style="font-size:16px;margin:15px 0 8px;padding:0;color:rgb(13,13,13);"><strong>Sentence 1:</strong></p>
<p style="font-size:14px;margin:0 0 8px 20px;padding:0;color:rgb(0,0,0);font-style:italic;line-height:1.6;">"Since then the world's richest man seems to have softened his stance: SpaceX, which recently merged with xAI, Mr Musk's artificial-intelligence lab, is this year expected to list its shares in the largest initial public offering (IPO) of all time."</p>
<p style="font-size:14px;margin:0 0 15px 20px;padding:0;color:rgb(100,100,100);line-height:1.8;"><strong>结构分析：</strong><br>• 主句：the world's richest man seems to have softened his stance<br>• 冒号后解释说明：SpaceX...is expected to list its shares<br>• which 引导非限制性定语从句，修饰 SpaceX<br>• Mr Musk's artificial-intelligence lab 是 xAI 的同位语</p>
<p style="font-size:14px;margin:0 0 15px 20px;padding:0;color:rgb(0,100,0);line-height:1.8;"><strong>译文：</strong>此后，这位世界首富似乎软化了他的立场：SpaceX 最近与马斯克的 AI 实验室 xAI 合并，预计今年将进行史上最大规模的首次公开募股。</p>

<p style="font-size:16px;margin:15px 0 8px;padding:0;color:rgb(13,13,13);"><strong>Sentence 2:</strong></p>
<p style="font-size:14px;margin:0 0 8px 20px;padding:0;color:rgb(0,0,0);font-style:italic;line-height:1.6;">"The number of listed American businesses has fallen by more than a third since the mid-1990s as the cost of compliance has risen and private markets have expanded and matured."</p>
<p style="font-size:14px;margin:0 0 15px 20px;padding:0;color:rgb(100,100,100);line-height:1.8;"><strong>结构分析：</strong><br>• 主句：The number...has fallen by more than a third<br>• since 引导时间状语：since the mid-1990s<br>• as 引导原因状语从句（两个并列）：the cost of compliance has risen 和 private markets have expanded and matured</p>
<p style="font-size:14px;margin:0 0 15px 20px;padding:0;color:rgb(0,100,0);line-height:1.8;"><strong>译文：</strong>自 1990 年代中期以来，美国上市公司数量减少了超过三分之一，原因是合规成本上升，私募市场扩大并成熟。</p>

<p style="font-size:16px;margin:15px 0 8px;padding:0;color:rgb(13,13,13);"><strong>Sentence 3:</strong></p>
<p style="font-size:14px;margin:0 0 8px 20px;padding:0;color:rgb(0,0,0);font-style:italic;line-height:1.6;">"The problem may be compounded by the change to the free-float rules, which would mechanically raise demand from passive funds while keeping the supply of shares constrained, pushing up the price."</p>
<p style="font-size:14px;margin:0 0 15px 20px;padding:0;color:rgb(100,100,100);line-height:1.8;"><strong>结构分析：</strong><br>• 主句：The problem may be compounded by the change<br>• which 引导非限制性定语从句，修饰 the change<br>• while 引导时间状语：while keeping the supply...constrained<br>• pushing up the price 是现在分词作结果状语</p>
<p style="font-size:14px;margin:0 0 15px 20px;padding:0;color:rgb(0,100,0);line-height:1.8;"><strong>译文：</strong>自由流通规则的变化可能会加剧这个问题，这将机械地提高被动基金的需求，同时保持股票供应受限，从而推高价格。</p>

<h2 style="font-size:18px;margin:30px 0 12px;padding:0;color:rgb(13,13,13);">💡 Writing Tips | 写作技巧</h2>

<p style="font-size:14px;margin:15px 0 8px;padding:0;color:rgb(13,13,13);"><strong>1. 使用冒号解释说明</strong></p>
<p style="font-size:14px;margin:0 0 15px 20px;padding:0;color:rgb(100,100,100);line-height:1.8;">原文：...softened his stance: SpaceX...is expected to list...<br>技巧：冒号后的内容解释说明前面的观点，使文章更清晰。</p>

<p style="font-size:14px;margin:15px 0 8px;padding:0;color:rgb(13,13,13);"><strong>2. 使用插入语补充信息</strong></p>
<p style="font-size:14px;margin:0 0 15px 20px;padding:0;color:rgb(100,100,100);line-height:1.8;">原文：SpaceX, which recently merged with xAI, Mr Musk's artificial-intelligence lab, is...<br>技巧：which 从句和同位语插入，在不打断主句的情况下提供额外信息。</p>

<p style="font-size:14px;margin:15px 0 8px;padding:0;color:rgb(13,13,13);"><strong>3. 使用现在分词表结果</strong></p>
<p style="font-size:14px;margin:0 0 15px 20px;padding:0;color:rgb(100,100,100);line-height:1.8;">原文：...pushing up the price<br>技巧：现在分词短语放在句末，表示前面动作的结果，使句子更紧凑。</p>

<h2 style="font-size:18px;margin:30px 0 12px;padding:0;color:rgb(13,13,13);">📝 IELTS/TOEFL Preparation | 备考建议</h2>

<p style="font-size:14px;margin:15px 0 8px;padding:0;color:rgb(13,13,13);"><strong>Reading:</strong></p>
<p style="font-size:14px;margin:0 0 15px 20px;padding:0;color:rgb(100,100,100);line-height:1.8;">• 本文适合雅思阅读 C1-C2 级别练习<br>• 重点练习：长难句分析、商业词汇积累<br>• 推荐计时阅读：3 分钟内完成全文阅读</p>

<p style="font-size:14px;margin:15px 0 8px;padding:0;color:rgb(13,13,13);"><strong>Writing:</strong></p>
<p style="font-size:14px;margin:0 0 15px 20px;padding:0;color:rgb(100,100,100);line-height:1.8;">• 学习使用冒号、插入语等高级句式<br>• 积累商业/经济类话题词汇（IPO, compliance, incumbent 等）<br>• 模仿文章的分析论证结构</p>

<p style="font-size:14px;margin:15px 0 8px;padding:0;color:rgb(13,13,13);"><strong>Listening:</strong></p>
<p style="font-size:14px;margin:0 0 15px 20px;padding:0;color:rgb(100,100,100);line-height:1.8;">• 可配合原文音频练习（如有）<br>• 重点听商业术语的发音和连读<br>• 练习记笔记和总结要点</p>

<p style="text-align:center;margin:35px 0 0;padding:15px;background-color:rgb(245,245,245);border-radius:5px;">
  <span style="font-size:14px;color:rgb(100,100,100);">📖 Keep learning and make progress every day!</span>
</p>
"""
    
    content_html += learning_content
    
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
    
    # 创建草稿（带封面图）
    article_data = {
        'title': full_title,
        'author': ARTICLE_META['author'],
        'digest': ARTICLE_META['digest'],
        'content': content_html,
        'content_source_url': ARTICLE_META['source_url'],
        'thumb_media_id': thumb_media_id,
        'show_cover_pic': 1
    }
    
    print("\n[INFO] 创建微信公众号草稿...")
    draft_result = create_draft(token, article_data)
    draft_media_id = draft_result.get('media_id')
    
    print("\n" + "=" * 60)
    print("[OK] 发布完成！")
    print("=" * 60)
    print(f"[TITLE] {full_title}")
    print(f"[DIGEST] {ARTICLE_META['digest']}")
    print(f"[COVER] ipo_cover.jpg ({thumb_media_id})")
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
