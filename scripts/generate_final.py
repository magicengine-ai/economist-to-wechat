# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
直接生成 HTML，不使用 JSON 文件
"""

from pathlib import Path

WORKSPACE = Path.home() / '.openclaw' / 'workspace'
TEMP_DIR = WORKSPACE / 'temp' / 'wechat_output'

SMALL_STYLE = 'border:0;font-style:inherit;font-variant-ligatures:none;font-variant-caps:small-caps;font-variant-numeric:normal;font-variant-east-asian:normal;font-variant-alternates:normal;font-variant-position:normal;font-variant-emoji:normal;font-weight:inherit;font-stretch:inherit;line-height:inherit;font-family:inherit;font-size:inherit;margin:0;padding:0;vertical-align:baseline;display:inline;text-transform:lowercase;'

# 中文翻译（直接写在脚本里，避免文件编码问题）
CHINESE = [
    "传统观点正在迅速形成。社交媒体使用会损害年轻人的心理健康，而生成式人工智能正在侵蚀他们的思考能力。这种焦虑是可以理解的。AI 工具以惊人的速度渗透到青少年的社交生活中，引发了对年龄限制、禁止\"AI 伴侣\"和更严格监管的呼声。但这场辩论假设 AI 对所有年轻人的影响大致相同，并且经常将使用时长作为风险的主要衡量标准。新兴证据表明情况恰恰相反。同样的技术可以为一些年轻人扩大机会，同时悄然取代其他人的人际支持。",
    "年轻人的社交和情感背景如何影响他们如何使用、何时使用以及为何使用生成式 AI 工具？这对政策制定意味着什么？我所在的健康数据公司团队在 2025 年 11 月对美国 13 至 24 岁年轻人进行了一项大型研究，探讨了这些问题。我们提出了 100 多个关于 AI 使用、对其生活影响以及更广泛的心理健康和生活背景的问题。",
    "我们发现，有些高频 AI 用户蓬勃发展，而有些低频用户却深陷困境。同样的工具根据用户的社会经济背景、触发压力的事件类型以及他们的\"人力资本\"（即他们拥有的技能和知识）而发挥截然不同的作用。年轻人使用 AI 的方式惊人地不同。",
    "对一些人来说，AI 充当了流动引擎。十分之一的年轻人是乐观的\"超级用户\"，将生成式 AI 视为学习和机会的工具，用它来构建技能、产生想法和探索新的职业道路。超过三分之二的人表示 AI 为他们开辟了新的机会，超过一半的人表示 AI 给了他们解决问题的信心，对世界更有希望。黑人青年和面临经济困难的人尤其可能属于这一群体，这表明在其他资源稀缺的地方，AI 可以扩大知识和机会的获取。",
    "对规模相似的另一个群体来说，AI 成为了线下缺失的社交和情感支持的替代品。这个令人担忧的群体在感到孤立时会向 AI 寻求对话、情感安慰和建议。这些高频用户报告了更高水平的痛苦，并且不成比例地可能面临欺凌、歧视或经济压力。AI 可能确实比完全没有支持要好。但通用系统并非为安全地扮演这一角色而设计。它们无法可靠地识别何时应该引导年轻人寻求专业帮助。",
    "还有一些人则完全与技术保持距离。这个群体约占年轻人的十分之一，不认为 AI 是实用工具。他们对其影响感到焦虑。他们的低参与度更多反映了他们更广泛的社会悲观情绪，而不是他们对技术的负面体验。我们发现白人和 LGBTQ+ 青年在这个群体中占比过高。对 LGBTQ+ 青年来说，AI 因监控和隐私问题加剧了他们的焦虑。",
    "然而，近一半的年轻人处于两者之间。他们务实地使用 AI，用它来探索、学习和解决问题，而不依赖它来获得身份认同或情感支持。强大的社会支持和归属感似乎起到了缓冲作用，使这些年轻人能够将 AI 视为工具，而不是人际联系的替代品。",
    "这对政策和实践意味着什么？规范访问或实施时间限制的直觉可能是错误的。最近的提议，从学校禁止 ChatGPT 到美国联邦 GUARD 法案，都反映了将减少接触作为主要安全机制的冲动。如果 AI 对一些年轻人来说是流动引擎，对另一些人是生产力工具，对缺乏支持的人是情感替代品，那么仅仅接触就是错误的监管变量。需要的是一种多管齐下的方法，补充这项技术融入年轻人生活的复杂方式，并在许多方面反映它。",
    "设计具有强大智能安全护栏的 AI 系统至关重要。公司有责任确保其系统不会让年轻用户暴露于有害互动，政策制定者应该追究他们的责任。一些政府，如加州和纽约，已经在朝这个方向迈进，提议要求更清晰的披露并限制情感操纵设计。但仅靠产品层面的修复是不够的。",
    "重要的问题是技术最终扮演的角色。政策应该关注 AI 何时开始取代人际支持，以及这种取代是否安全。这意味着建立从 AI 工具到人际关怀的路径，例如与心理健康服务的便捷连接，并为学校和家庭提供素养，帮助他们引导年轻人使用这些系统。",
    "值得信任的成年人是其中的核心。父母认为孩子使用 AI 的目的与实际使用方式之间往往存在脱节。然而，父母和值得信任的成年人仍然是最重要的支持促进者。帮助他们就 AI 进行更知情的对话，而不仅仅是限制，将是关键。专家建议，这些对话应该专注于帮助青少年理解 AI 能做什么和不能做什么，讨论隐私风险，并鼓励对 AI 回复进行批判性思考。从我们在社交媒体使用方面未能装备父母的教训中，我们可以学到重要的经验。",
    "简而言之，辩论需要转变。与其只问年轻人在 AI 上花了多少时间，不如问这项技术如何融入塑造他们生活的社会环境。生成式 AI 本身不会决定年轻人的福祉。但它可能会揭示并有时放大他们周围人际支持系统的优势或缺失。■"
]

def main():
    # 从 JSON 读取英文原文
    import json
    with open(WORKSPACE / 'economist-to-wechat' / 'scripts' / 'young_ai_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    paragraphs = data['paragraphs']
    
    # 构建 HTML
    html = '''<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>经济学人 | 年轻人如何使用 AI 比时长更重要 | How the young use AI matters</title>
</head>
<body>

<h1 style="border:0;font-style:normal;font-variant:oldstyle-nums;font-weight:400;font-stretch:inherit;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;margin:0;padding:0;color:rgb(13,13,13);text-align:start;"><span leaf="">That undermines the case for blanket bans or time limits, writes Sema Sgaier</span></h1>

<p style="border:0;font-style:normal;font-variant:oldstyle-nums;font-weight:400;font-stretch:inherit;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;margin:0 0 8px;padding:0;color:rgb(13,13,13);text-align:start;"><span leaf="" style="border:0;font-variant-alternates:inherit;font-variant-numeric:inherit;font-variant-east-asian:inherit;font-variant-position:inherit;font-variant-emoji:inherit;font-stretch:inherit;line-height:inherit;font-optical-sizing:inherit;font-size-adjust:inherit;font-kerning:inherit;font-feature-settings:inherit;font-variation-settings:inherit;font-language-override:inherit;margin:0;padding:0;vertical-align:baseline;color:rgb(24,32,38);font-size:14px;" segoe="segoe" ui="ui" sans="sans" neue="neue">这削弱了全面禁令或时间限制的合理性</span></p>
'''
    
    for i, para in enumerate(paragraphs):
        is_first = (i == 0)
        inner_html = para['innerHTML']
        
        # 转换 small 标签
        html_content = inner_html.replace('<i>', '').replace('</i>', '')
        import re
        def replace_small(match):
            content = match.group(1)
            return f'<small style="{SMALL_STYLE}"><span leaf="">{content}</span></small>'
        html_content = re.sub(r'<small>(.*?)</small>', replace_small, html_content)
        html_content = html_content.replace('&', '&amp;')
        html_content = re.sub(r'<span[^>]*class="ufinish"[^>]*>■</span>', '<span style="color:rgb(227,18,11)">■</span>', html_content)
        
        # 处理首字母大写
        if is_first:
            html_content = html_content.replace(
                '<span data-caps="initial">',
                '<span data-caps="initial" style="border:0;font-style:inherit;font-variant:inherit;font-weight:inherit;font-stretch:inherit;line-height:1;font-family:inherit;font-size:3.5rem;margin:0 0.2rem 0 0;padding:0;vertical-align:baseline;float:left;height:3.25rem;text-transform:uppercase;">'
            )
            margin = "0"
        else:
            margin = "0.875rem 0 0"
        
        # 添加英文段落
        html += f'<p data-component="paragraph" style="border:0;font-style:normal;font-variant:oldstyle-nums;font-weight:400;font-stretch:inherit;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;margin:{margin};padding:0;color:rgb(13,13,13);text-align:start;"><span leaf="" style="color:rgb(13,13,13);font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;font-style:normal;font-variant-ligatures:normal;font-variant-caps:normal;font-weight:400;letter-spacing:normal;text-align:start;text-indent:0px;text-transform:none;-webkit-text-stroke-width:0px;background-color:rgb(255,255,255);float:none;display:inline!important;">{html_content}</span></p>\n'
        
        # 添加中文段落
        chinese_margin = "0 0 8px" if is_first else "8px 0 16px"
        html += f'<p style="border:0;font-style:normal;font-variant:oldstyle-nums;font-weight:400;font-stretch:inherit;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;margin:{chinese_margin};padding:0;color:rgb(13,13,13);text-align:start;"><span leaf="" style="border:0;font-variant-alternates:inherit;font-variant-numeric:inherit;font-variant-east-asian:inherit;font-variant-position:inherit;font-variant-emoji:inherit;font-stretch:inherit;line-height:inherit;font-optical-sizing:inherit;font-size-adjust:inherit;font-kerning:inherit;font-feature-settings:inherit;font-variation-settings:inherit;font-language-override:inherit;margin:0;padding:0;vertical-align:baseline;color:rgb(24,32,38);font-size:14px;" segoe="segoe" ui="ui" sans="sans" neue="neue">{CHINESE[i]}</span></p>\n'
    
    html += '''
<p style="display:none;"><mp-style-type data-value="10000"></mp-style-type></p>
</body>
</html>
'''
    
    # 保存文件（UTF-8 无 BOM）
    output_path = TEMP_DIR / 'young_ai_final.html'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 使用 binary write 确保 UTF-8 无 BOM
    with open(output_path, 'wb') as f:
        f.write(html.encode('utf-8'))
    
    print(f"[OK] HTML 文件已保存：{output_path}")
    print(f"段落数：{len(paragraphs)} 段")
    print(f"文件大小：{len(html.encode('utf-8'))} 字节")
    
    # 验证中文内容
    print(f"\n验证中文内容:")
    print(f"第一段中文前 50 字：{CHINESE[0][:50]}")

if __name__ == '__main__':
    main()
