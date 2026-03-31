# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
从经济学人网站抓取文章并转换为微信公众号格式
直接使用原文的 HTML 结构（body-text 标签和 initial/small 标签）
"""

import json
from pathlib import Path

# 配置
WORKSPACE = Path.home() / '.openclaw' / 'workspace'
TEMP_DIR = WORKSPACE / 'temp' / 'wechat_output'

# 从浏览器获取的原文数据（19 个 body-text 段落）
ORIGINAL_PARAGRAPHS = [
    # index 0: 副标题
    {
        'has_initial': False,
        'text': 'Its lead over the West is only set to widen',
        'innerHTML': 'Its lead over the West is only set to widen'
    },
    # index 1: 正文第 1 段（带首字母大写）
    {
        'has_initial': True,
        'text': 'Is IT POSSIBLE that the United States falls behind China?" Jensen Huang...',
        'innerHTML': """<span data-caps="initial">I</span><small>s IT POSSIBLE</small> that the United States falls behind China?" Jensen Huang, the boss of Nvidia, asked himself during a question-and-answer session about artificial intelligence late last year. "The answer is absolutely yes." That may seem surprising—for much of the past decade America has been comfortably ahead in the <small>AI</small> race, home to the most advanced companies producing frontier models. Its engineers have access to deep pools of capital as well as a regular supply of Nvidia's cutting-edge chips. But Mr Huang's concern related to an equally important ingredient of innovation: human talent."""
    },
    # index 2: 正文第 2 段
    {
        'has_initial': False,
        'innerHTML': """Until recently, most leading <small>AI</small> research was produced by experts based in the West. That is changing. In 2025, for the first time, more studies presented at the world's top <small>AI</small> conference had lead authors based in China than in either America or Europe. To better understand the international ebbs and flows of <small>AI</small> talent, <i>The Economist</i> tracked the education histories of researchers who presented papers at the December 2025 edition of the Conference on Neural Information Processing Systems (Neur<small>IPS</small>), the world's largest and most prestigious <small>AI</small> gathering. More than 21,000 papers were submitted to Neur<small>IPS</small>, of which roughly a quarter were accepted. MacroPolo, a now-shuttered think tank, analysed the change in educational background of Neur<small>IPS</small> authors in 2019 and 2022. We applied their method to a random sample of 600 papers (authored by almost 4,000 researchers) from 2025."""
    },
    # index 4: 正文第 3 段
    {
        'has_initial': False,
        'innerHTML': """In 2019, 29% of <small>AI</small> researchers who presented at Neur<small>IPS</small> began their careers in China."""
    },
    # index 5: 正文第 4 段
    {
        'has_initial': False,
        'innerHTML': """By 2025 half did. Over the same period, the share who started out in America fell from 20% to 12%."""
    },
    # index 6: 正文第 5 段
    {
        'has_initial': False,
        'innerHTML': """Moreover, fewer Chinese undergraduates leave upon graduation. By 2025 three fifths of <small>AI</small> researchers continued their studies in China."""
    },
    # index 8: 正文第 6 段
    {
        'has_initial': False,
        'innerHTML': """Nine of the top ten institutions where authors from the 2025 conference earned their undergraduate degrees were in China. Graduates of Tsinghua University alone accounted for 4% of researchers at Neur<small>IPS</small>. <small>MIT</small>, the leading American institution, produced 1%."""
    },
    # index 9: 正文第 7 段
    {
        'has_initial': False,
        'innerHTML': """The analysis also shows the extent to which America's <small>AI</small> efforts rely on Chinese-born researchers. Among authors affiliated with American institutions, roughly 35% have a Chinese undergraduate degree (as many as have an American one). That being said, Neur<small>IPS</small> may not be entirely representative of the field. Chinese researchers might feel stronger incentives to present at the conference: to win promotions at academic institutions, for example, scientists often need top conference papers on their <small>CV</small>. What's more, China's culture of open-source models may encourage its authors to publish in academic forums, whereas America's leading talent is increasingly concentrated in secretive frontier labs."""
    },
    # index 10: 正文第 8 段
    {
        'has_initial': False,
        'innerHTML': """There are other measures by which the importance of Chinese researchers to America can be gauged. When Meta, a tech company, announced the researchers staffing its new "superintelligence lab", in June, a leaked list revealed that half were described as being from China. <i>The Economist</i>'s analysis of 483 contributors to Open<small>AI</small>'s <small>GPT</small>-5 (which includes <small>AI</small> researchers as well as marketing, design and leadership staff) found that 15% had at least one degree from a Chinese institution."""
    },
    # index 11: 正文第 9 段
    {
        'has_initial': False,
        'innerHTML': "China is increasingly holding on to its <small>AI</small> talent. According to Digital Science, a data firm, China now has more active <small>AI</small> researchers than America, Britain and Europe combined—though it still trails the West per head of population. What's more, China's cohort skews younger: 47% are students, compared with about 30% in the West. The country also prioritises education in science, technology, engineering and maths (<small>STEM</small>): around two-fifths of Chinese university students study <small>STEM</small> subjects, roughly double America's share."
    },
    # index 12: 正文第 10 段
    {
        'has_initial': False,
        'innerHTML': "Not all of these graduates will produce frontier innovations, but scale matters. A large pool of <small>AI</small>-savvy researchers increases the chance of breakthroughs and means new technologies spread faster. \"China is creating this high-quality, highly trained workforce who is <small>AI</small>-sensitive,\" says Daniel Hook, the boss of Digital Science. \"That's just going to mean so many companies coming out of China in the future.\""
    },
    # index 13: 正文第 11 段
    {
        'has_initial': False,
        'innerHTML': "Chinese boffins are increasingly choosing to stay in the country. In 2019 roughly a third of Neur<small>IPS</small> authors who had completed their undergraduate degrees in China remained there. By 2022 that share had risen to 58%; in 2025 it reached 68%. Some of the country's best innovations have come from entirely home-grown talent—none of the core contributors to DeepSeek <small>R</small>1, a Chinese model that stunned rivals when it was released in January 2025, held degrees from outside of China."
    },
    # index 14: 正文第 12 段
    {
        'has_initial': False,
        'innerHTML': "These changes reflect both pull and push. Chinese universities are increasingly ranked among the best in the world. At the same time, initiatives to lure talented researchers back to China, such as the Qiming Plan, offer salaries of more than 700,000 yuan ($100,000), generous research grants and help with housing."
    },
    # index 15: 正文第 13 段
    {
        'has_initial': False,
        'innerHTML': "At the same time America has become a less attractive destination. Funding cuts and visa uncertainty have unsettled would-be applicants, as has increasing suspicion of their loyalties. Last year Purdue University rescinded offers to more than 100 graduate students, most of them Chinese, after being asked by lawmakers to document researchers' ties to institutions in China. At American <small>AI</small> meetings some Chinese researchers feel the need to clarify they are not corporate spies."
    },
    # index 16: 正文第 14 段
    {
        'has_initial': False,
        'innerHTML': "More are therefore heading home. In 2019 just 12% of Chinese Neur<small>IPS</small> researchers who had earned graduate degrees abroad had returned to China. By 2025 that share had more than doubled to 28%."
    },
    # index 17: 正文第 15 段
    {
        'has_initial': False,
        'innerHTML': "<i>The Economist</i> spoke with Chinese-born early-career researchers who have recently relocated back home from America, or have moved back and forth between the two countries. Some still consider America to have a stronger research environment or complain of fierce competition and long hours at China's fast-growing firms. Yet they said on balance a strong job market, interesting opportunities and proximity to family now outweigh those drawbacks."
    },
    # index 18: 正文第 16 段
    {
        'has_initial': False,
        'innerHTML': "America's appeal has not vanished. It still draws more international talent than anywhere else and most Chinese researchers who complete graduate degrees in America stay on to work. Following up on a sample of Chinese-born, America-based Neur<small>IPS</small> authors from the 2019 conference, 87% were still there in 2025. \"Long-standing institutions just don't disappear overnight,\" says Matt Sheehan, of the Carnegie Endowment for International Peace, who performed the research and worked on the original MacroPolo analysis."
    },
    # index 19: 正文第 17 段（带结束符号）
    {
        'has_initial': False,
        'innerHTML': "But the numbers increasingly favour China. Using the authors of Neur<small>IPS</small> papers as a metric, around 37% of the world's top <small>AI</small> researchers now work in Chinese organisations, compared with 32% in American ones. If the trend of the past decade continues, by 2028 top Chinese-based researchers could outnumber American-based ones by two to one. According to Mr Huang, for a country to lead in <small>AI</small> \"winning developers is everything\". The battle for talent looks increasingly one-sided.<span data-ornament=\"ufinish\">■</span>"
    }
]


def convert_inner_html_to_wechat(inner_html, is_first_para=False):
    """
    将原文的 innerHTML 转换为微信公众号格式
    
    Args:
        inner_html: 原文的 innerHTML（包含 small、i 等标签）
        is_first_para: 是否为第一段（需要首字母大写格式）
    
    Returns:
        转换后的 HTML
    """
    # 替换 <i> 标签为普通文本（微信不支持）
    html = inner_html.replace('<i>', '').replace('</i>', '')
    
    # 替换 <small> 标签为带样式的 small 标签
    SMALL_STYLE = 'border:0;font-style:inherit;font-variant-ligatures:none;font-variant-caps:small-caps;font-variant-numeric:normal;font-variant-east-asian:normal;font-variant-alternates:normal;font-variant-position:normal;font-variant-emoji:normal;font-weight:inherit;font-stretch:inherit;line-height:inherit;font-family:inherit;font-size:inherit;margin:0;padding:0;vertical-align:baseline;display:inline;text-transform:lowercase;'
    
    import re
    def replace_small(match):
        content = match.group(1)
        return f'<small style="{SMALL_STYLE}"><span leaf="">{content}</span></small>'
    
    html = re.sub(r'<small>(.*?)</small>', replace_small, html)
    
    # 替换结束符号
    html = html.replace('<span data-ornament="ufinish">■</span>', '<span style="color:rgb(227,18,11)">■</span>')
    
    return html


def format_first_paragraph(inner_html):
    """格式化第一段（带首字母大写）"""
    # 原文已经有 <span data-caps="initial">I</span><small>s IT POSSIBLE</small> 结构
    # 直接使用并添加样式
    
    SMALL_STYLE = 'border:0;font-style:inherit;font-variant-ligatures:none;font-variant-caps:small-caps;font-variant-numeric:normal;font-variant-east-asian:normal;font-variant-alternates:normal;font-variant-position:normal;font-variant-emoji:normal;font-weight:inherit;font-stretch:inherit;line-height:inherit;font-family:inherit;font-size:inherit;margin:0;padding:0;vertical-align:baseline;display:inline;text-transform:lowercase;'
    
    import re
    
    # 转换 innerHTML
    html = convert_inner_html_to_wechat(inner_html)
    
    # 替换 initial span 的样式
    html = html.replace(
        '<span data-caps="initial">',
        '<span data-caps="initial" style="border:0;font-style:inherit;font-variant:inherit;font-weight:inherit;font-stretch:inherit;line-height:1;font-family:inherit;font-size:3.5rem;margin:0 0.2rem 0 0;padding:0;vertical-align:baseline;float:left;height:3.25rem;text-transform:uppercase;">'
    )
    
    # 替换 small 标签（第一个单词）
    html = re.sub(
        r'<small style="[^"]*"><span leaf="">',
        f'<small style="{SMALL_STYLE}"><span leaf="">',
        html,
        count=1  # 只替换第一个
    )
    
    return f'<p data-component="paragraph" style="border:0;font-style:normal;font-variant:oldstyle-nums;font-weight:400;font-stretch:inherit;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;margin:0;padding:0;color:rgb(13,13,13);text-align:start;">{html}</span></p>'


def format_paragraph(inner_html):
    """格式化普通段落"""
    html = convert_inner_html_to_wechat(inner_html)
    
    return f'<p data-component="paragraph" style="border:0;font-style:normal;font-variant:oldstyle-nums;font-weight:400;font-stretch:inherit;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;margin:0.875rem 0 0;padding:0;color:rgb(13,13,13);text-align:start;"><span leaf="" style="color:rgb(13,13,13);font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;font-style:normal;font-variant-ligatures:normal;font-variant-caps:normal;font-weight:400;letter-spacing:normal;text-align:start;text-indent:0px;text-transform:none;-webkit-text-stroke-width:0px;background-color:rgb(255,255,255);float:none;display:inline!important;">{html}</span></p>'


def main():
    print("=" * 60)
    print("生成经济学人文章 HTML（根据原文 body-text 标签）")
    print("=" * 60)
    
    # 构建 HTML
    print("\n[INFO] 构建 HTML...")
    html_parts = []
    
    # 副标题（英文）- index 0
    html_parts.append(f'<h1 style="border:0;font-style:normal;font-variant:oldstyle-nums;font-weight:400;font-stretch:inherit;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;margin:0;padding:0;color:rgb(13,13,13);text-align:start;"><span leaf="">{ORIGINAL_PARAGRAPHS[0]["innerHTML"]}</span></h1>')
    
    # 副标题（中文）
    html_parts.append('<p style="border:0;font-style:normal;font-variant:oldstyle-nums;font-weight:400;font-stretch:inherit;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;margin:0 0 8px;padding:0;color:rgb(13,13,13);text-align:start;"><span leaf="" style="border:0;font-variant-alternates:inherit;font-variant-numeric:inherit;font-variant-east-asian:inherit;font-variant-position:inherit;font-variant-emoji:inherit;font-stretch:inherit;line-height:inherit;font-optical-sizing:inherit;font-size-adjust:inherit;font-kerning:inherit;font-feature-settings:inherit;font-variation-settings:inherit;font-language-override:inherit;margin:0;padding:0;vertical-align:baseline;color:rgb(24,32,38);font-size:14px;" segoe="segoe" ui="ui" sans="sans" neue="neue">其对西方的领先优势只会不断扩大</span></p>')
    
    # 处理正文段落（从 index 1 开始）
    for i, para in enumerate(ORIGINAL_PARAGRAPHS[1:], start=1):
        if para['has_initial']:
            # 第一段 - 带首字母大写
            html_parts.append(format_first_paragraph(para['innerHTML']))
            print(f"[INFO] 段落 {i}: 使用首字母大写格式（原文有 initial 标签）")
        else:
            # 普通段落
            html_parts.append(format_paragraph(para['innerHTML']))
            print(f"[INFO] 段落 {i}: 普通格式")
        
        # 添加中文翻译占位
        html_parts.append(f'<p style="border:0;font-style:normal;font-variant:oldstyle-nums;font-weight:400;font-stretch:inherit;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;margin:8px 0 16px;padding:0;color:rgb(13,13,13);text-align:start;"><span leaf="" style="border:0;font-variant-alternates:inherit;font-variant-numeric:inherit;font-variant-east-asian:inherit;font-variant-position:inherit;font-variant-emoji:inherit;font-stretch:inherit;line-height:inherit;font-optical-sizing:inherit;font-size-adjust:inherit;font-kerning:inherit;font-feature-settings:inherit;font-variation-settings:inherit;font-language-override:inherit;margin:0;padding:0;vertical-align:baseline;color:rgb(24,32,38);font-size:14px;" segoe="segoe" ui="ui" sans="sans" neue="neue">[中文翻译待添加]</span></p>')
    
    # 隐藏样式标签
    html_parts.append('<p style="display:none;"><mp-style-type data-value="10000"></mp-style-type></p>')
    
    # 保存 HTML 文件
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    output_file = TEMP_DIR / 'economist_from_original.html'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('<!DOCTYPE html>\n')
        f.write('<html>\n')
        f.write('<head>\n')
        f.write('  <meta charset="UTF-8">\n')
        f.write('  <title>经济学人 - China is winning the AI talent race</title>\n')
        f.write('</head>\n')
        f.write('<body>\n')
        f.write('\n'.join(html_parts))
        f.write('\n</body>\n')
        f.write('</html>\n')
    
    print(f"\n[OK] HTML 文件已保存到：{output_file}")
    print(f"[INFO] 文件大小：{output_file.stat().st_size} bytes")
    print(f"[INFO] 段落数量：{len(ORIGINAL_PARAGRAPHS) - 1}（不含副标题）")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        exit(1)
