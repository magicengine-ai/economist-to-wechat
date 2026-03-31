# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
从经济学人网站抓取文章并转换为微信公众号格式
使用浏览器工具抓取页面内容
"""

import json
import re
from pathlib import Path

# 配置
WORKSPACE = Path.home() / '.openclaw' / 'workspace'
TEMP_DIR = WORKSPACE / 'temp' / 'wechat_output'

# 常见缩写词列表（自动检测并添加 <small>标签）
ABBREVIATIONS = [
    'AI', 'PR', 'STEM', 'GDP', 'CEO', 'CFO', 'COO', 'CTO', 'CIO',
    'IMF', 'OECD', 'WTO', 'UN', 'US', 'UK', 'EU', 'NATO', 'OPEC',
    'IRGC', 'NIOC', 'Basij', 'TS', 'NeurIPS', 'MIT', 'CV'
]

# 完整的 <small> 标签样式
SMALL_STYLE = 'border:0;font-style:inherit;font-variant-ligatures:none;font-variant-caps:small-caps;font-variant-numeric:normal;font-variant-east-asian:normal;font-variant-alternates:normal;font-variant-position:normal;font-variant-emoji:normal;font-weight:inherit;font-stretch:inherit;line-height:inherit;font-family:inherit;font-size:inherit;margin:0;padding:0;vertical-align:baseline;display:inline;text-transform:lowercase;'


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


def format_paragraph(para_text):
    """格式化普通段落"""
    # 处理缩写词
    para_processed = wrap_abbreviations(para_text)
    
    return f'<p data-component="paragraph" style="border:0;font-style:normal;font-variant:oldstyle-nums;font-weight:400;font-stretch:inherit;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;margin:0.875rem 0 0;padding:0;color:rgb(13,13,13);text-align:start;"><span leaf="" style="color:rgb(13,13,13);font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;font-style:normal;font-variant-ligatures:normal;font-variant-caps:normal;font-weight:400;letter-spacing:normal;text-align:start;text-indent:0px;text-transform:none;-webkit-text-stroke-width:0px;background-color:rgb(255,255,255);float:none;display:inline!important;">{para_processed}</span></p>'


def main():
    """
    从浏览器快照中提取的文章段落
    
    根据页面内容，这篇文章有 11 个段落：
    - 第 1 段：首字母大写 I（Is）
    - 第 2-11 段：普通段落
    """
    
    # 从浏览器快照手动提取的段落
    paragraphs = [
        # 第 1 段 - 带首字母大写
        '"Is it possible that the United States falls behind China?" Jensen Huang, the boss of Nvidia, asked himself during a question-and-answer session about artificial intelligence late last year. "The answer is absolutely yes." That may seem surprising—for much of the past decade America has been comfortably ahead in the AI race, home to the most advanced companies producing frontier models. Its engineers have access to deep pools of capital as well as a regular supply of Nvidia\'s cutting-edge chips. But Mr Huang\'s concern related to an equally important ingredient of innovation: human talent.',
        
        # 第 2 段
        'Until recently, most leading AI research was produced by experts based in the West. That is changing. In 2025, for the first time, more studies presented at the world\'s top AI conference had lead authors based in China than in either America or Europe. To better understand the international ebbs and flows of AI talent, The Economist tracked the education histories of researchers who presented papers at the December 2025 edition of the Conference on Neural Information Processing Systems (NeurIPS), the world\'s largest and most prestigious AI gathering. More than 21,000 papers were submitted to NeurIPS, of which roughly a quarter were accepted. MacroPolo, a now-shuttered think tank, analysed the change in educational background of NeurIPS authors in 2019 and 2022. We applied their method to a random sample of 600 papers (authored by almost 4,000 researchers) from 2025.',
        
        # 第 3 段
        'In 2019, 29% of AI researchers who presented at NeurIPS began their careers in China. By 2025 half did. Over the same period, the share who started out in America fell from 20% to 12%. Moreover, fewer Chinese undergraduates leave upon graduation. By 2025 three fifths of AI researchers continued their studies in China.',
        
        # 第 4 段
        'Nine of the top ten institutions where authors from the 2025 conference earned their undergraduate degrees were in China. Graduates of Tsinghua University alone accounted for 4% of researchers at NeurIPS. MIT, the leading American institution, produced 1%.',
        
        # 第 5 段
        'The analysis also shows the extent to which America\'s AI efforts rely on Chinese-born researchers. Among authors affiliated with American institutions, roughly 35% have a Chinese undergraduate degree (as many as have an American one). That being said, NeurIPS may not be entirely representative of the field. Chinese researchers might feel stronger incentives to present at the conference: to win promotions at academic institutions, for example, scientists often need top conference papers on their CV. What\'s more, China\'s culture of open-source models may encourage its authors to publish in academic forums, whereas America\'s leading talent is increasingly concentrated in secretive frontier labs.',
        
        # 第 6 段
        'There are other measures by which the importance of Chinese researchers to America can be gauged. When Meta, a tech company, announced the researchers staffing its new "superintelligence lab", in June, a leaked list revealed that half were described as being from China. The Economist\'s analysis of 483 contributors to OpenAI\'s GPT-5 (which includes AI researchers as well as marketing, design and leadership staff) found that 15% had at least one degree from a Chinese institution.',
        
        # 第 7 段
        'China is increasingly holding on to its AI talent. According to Digital Science, a data firm, China now has more active AI researchers than America, Britain and Europe combined—though it still trails the West per head of population. What\'s more, China\'s cohort skews younger: 47% are students, compared with about 30% in the West. The country also prioritises education in science, technology, engineering and maths (STEM): around two-fifths of Chinese university students study STEM subjects, roughly double America\'s share.',
        
        # 第 8 段
        'Not all of these graduates will produce frontier innovations, but scale matters. A large pool of AI-savvy researchers increases the chance of breakthroughs and means new technologies spread faster. "China is creating this high-quality, highly trained workforce who is AI-sensitive," says Daniel Hook, the boss of Digital Science. "That\'s just going to mean so many companies coming out of China in the future."',
        
        # 第 9 段
        'Chinese boffins are increasingly choosing to stay in the country. In 2019 roughly a third of NeurIPS authors who had completed their undergraduate degrees in China remained there. By 2022 that share had risen to 58%; in 2025 it reached 68%. Some of the country\'s best innovations have come from entirely home-grown talent—none of the core contributors to DeepSeek R1, a Chinese model that stunned rivals when it was released in January 2025, held degrees from outside of China.',
        
        # 第 10 段
        'These changes reflect both pull and push. Chinese universities are increasingly ranked among the best in the world. At the same time, initiatives to lure talented researchers back to China, such as the Qiming Plan, offer salaries of more than 700,000 yuan ($100,000), generous research grants and help with housing. At the same time America has become a less attractive destination. Funding cuts and visa uncertainty have unsettled would-be applicants, as has increasing suspicion of their loyalties. Last year Purdue University rescinded offers to more than 100 graduate students, most of them Chinese, after being asked by lawmakers to document researchers\' ties to institutions in China. At American AI meetings some Chinese researchers feel the need to clarify they are not corporate spies.',
        
        # 第 11 段 - 带结束符号
        'More are therefore heading home. In 2019 just 12% of Chinese NeurIPS researchers who had earned graduate degrees abroad had returned to China. By 2025 that share had more than doubled to 28%. The Economist spoke with Chinese-born early-career researchers who have recently relocated back home from America, or have moved back and forth between the two countries. Some still consider America to have a stronger research environment or complain of fierce competition and long hours at China\'s fast-growing firms. Yet they said on balance a strong job market, interesting opportunities and proximity to family now outweigh those drawbacks. America\'s appeal has not vanished. It still draws more international talent than anywhere else and most Chinese researchers who complete graduate degrees in America stay on to work. Following up on a sample of Chinese-born, America-based NeurIPS authors from the 2019 conference, 87% were still there in 2025. "Long-standing institutions just don\'t disappear overnight," says Matt Sheehan, of the Carnegie Endowment for International Peace, who performed the research and worked on the original MacroPolo analysis. But the numbers increasingly favour China. Using the authors of NeurIPS papers as a metric, around 37% of the world\'s top AI researchers now work in Chinese organisations, compared with 32% in American ones. If the trend of the past decade continues, by 2028 top Chinese-based researchers could outnumber American-based ones by two to one. According to Mr Huang, for a country to lead in AI "winning developers is everything". The battle for talent looks increasingly one-sided. <span style="color:rgb(227,18,11)">■</span>'
    ]
    
    print("=" * 60)
    print("生成经济学人文章 HTML（11 段完整版）")
    print("=" * 60)
    
    # 构建 HTML
    print("\n[INFO] 构建 HTML...")
    html_parts = []
    
    # 副标题（英文）
    html_parts.append('<h1 style="border:0;font-style:normal;font-variant:oldstyle-nums;font-weight:400;font-stretch:inherit;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;margin:0;padding:0;color:rgb(13,13,13);text-align:start;"><span leaf="">Its lead over the West is only set to widen</span></h1>')
    
    # 副标题（中文）
    html_parts.append('<p style="border:0;font-style:normal;font-variant:oldstyle-nums;font-weight:400;font-stretch:inherit;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;margin:0 0 8px;padding:0;color:rgb(13,13,13);text-align:start;"><span leaf="" style="border:0;font-variant-alternates:inherit;font-variant-numeric:inherit;font-variant-east-asian:inherit;font-variant-position:inherit;font-variant-emoji:inherit;font-stretch:inherit;line-height:inherit;font-optical-sizing:inherit;font-size-adjust:inherit;font-kerning:inherit;font-feature-settings:inherit;font-variation-settings:inherit;font-language-override:inherit;margin:0;padding:0;vertical-align:baseline;color:rgb(24,32,38);font-size:14px;" segoe="segoe" ui="ui" sans="sans" neue="neue">其对西方的领先优势只会不断扩大</span></p>')
    
    # 处理段落
    for i, para_text in enumerate(paragraphs):
        if i == 0:
            # 第一段 - 带首字母大写
            html_parts.append(format_first_paragraph(para_text))
            print(f"[INFO] 段落 {i+1}: 使用首字母大写格式")
        else:
            # 普通段落
            html_parts.append(format_paragraph(para_text))
            print(f"[INFO] 段落 {i+1}: 普通格式")
        
        # 添加中文翻译占位
        html_parts.append(f'<p style="border:0;font-style:normal;font-variant:oldstyle-nums;font-weight:400;font-stretch:inherit;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;margin:8px 0 16px;padding:0;color:rgb(13,13,13);text-align:start;"><span leaf="" style="border:0;font-variant-alternates:inherit;font-variant-numeric:inherit;font-variant-east-asian:inherit;font-variant-position:inherit;font-variant-emoji:inherit;font-stretch:inherit;line-height:inherit;font-optical-sizing:inherit;font-size-adjust:inherit;font-kerning:inherit;font-feature-settings:inherit;font-variation-settings:inherit;font-language-override:inherit;margin:0;padding:0;vertical-align:baseline;color:rgb(24,32,38);font-size:14px;" segoe="segoe" ui="ui" sans="sans" neue="neue">[中文翻译待添加]</span></p>')
    
    # 隐藏样式标签
    html_parts.append('<p style="display:none;"><mp-style-type data-value="10000"></mp-style-type></p>')
    
    # 保存 HTML 文件
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    output_file = TEMP_DIR / 'economist_11paras.html'
    
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
    print(f"[INFO] 段落数量：{len(paragraphs)}")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        exit(1)
