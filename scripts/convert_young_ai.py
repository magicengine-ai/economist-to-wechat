# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
转换"How the young use AI matters"为微信公众号格式
使用原文的 innerHTML 和 small 标签
"""

import json
import re
from pathlib import Path

WORKSPACE = Path.home() / '.openclaw' / 'workspace'
TEMP_DIR = WORKSPACE / 'temp' / 'wechat_output'

# small 标签完整样式
SMALL_STYLE = 'border:0;font-style:inherit;font-variant-ligatures:none;font-variant-caps:small-caps;font-variant-numeric:normal;font-variant-east-asian:normal;font-variant-alternates:normal;font-variant-position:normal;font-variant-emoji:normal;font-weight:inherit;font-stretch:inherit;line-height:inherit;font-family:inherit;font-size:inherit;margin:0;padding:0;vertical-align:baseline;display:inline;text-transform:lowercase;'

# 从浏览器获取的原文数据（12 段）
ORIGINAL_PARAGRAPHS = [
    {
        'has_initial': True,
        'innerHTML': '<span data-caps="initial">C</span><small>ONVENTIONAL WISDOM</small> is forming quickly. Social-media use damages young people's mental health and generative artificial intelligence is now eroding their ability to think. The anxiety is understandable. <small>AI</small> tools have spread through teenage social lives with extraordinary speed, prompting calls for age limits, bans on "<small>AI</small> companions" and tighter guardrails. But the debate assumes that <small>AI</small> affects all young people in broadly the same way and often treats time spent using it as the main measure of risk. Emerging evidence suggests the opposite. The same technology can expand opportunity for some youngsters while quietly replacing human support for others.'
    },
    {
        'has_initial': False,
        'innerHTML': 'How might a young person's social and emotional context play a role in how, when and why they use generative-<small>AI</small> tools? And what does this mean for how policies should be shaped? A team at the health-data firm I run addressed these questions in a large study of 13- to 24-year-olds in America, conducted in November 2025. We asked over 100 questions about <small>AI</small> use, its impacts on their lives, and their broader mental health and life context.'
    },
    {
        'has_initial': False,
        'innerHTML': 'We find high-frequency <small>AI</small> users who are thriving and low-frequency users who are in deep distress. The same tool functions radically differently depending on a user's socioeconomic context, the types of events that trigger stress for them and their "human capital": the skills and knowledge they possess. Young people use <small>AI</small> in strikingly different ways.'
    },
    {
        'has_initial': False,
        'innerHTML': 'For some, <small>AI</small> functions as a mobility engine. One in ten young people are optimistic "power users" and treat generative <small>AI </small>as a tool for learning and opportunity, using it to build skills, generate ideas and explore new career paths. Over two-thirds of this group say <small>AI </small>opens new opportunities, while more than half say it gives them confidence to solve problems and feel more hopeful about the world. Black youth and those facing economic hardship are particularly likely to fall into this group, suggesting that <small>AI</small> can expand access to knowledge and opportunity where other resources are scarce.'
    },
    {
        'has_initial': False,
        'innerHTML': 'For a similar-sized group, <small>AI</small> becomes a substitute for social and emotional support that is missing offline. This worrying group turns to <small>AI</small> for conversation, emotional reassurance and advice when they feel isolated. These high-frequency users report higher levels of distress and are disproportionately likely to face bullying, discrimination or financial strain. <small>AI</small> may indeed be better than no support at all. But general-purpose systems are not designed to play this role safely. They cannot reliably recognise when to direct a young person to professional help.'
    },
    {
        'has_initial': False,
        'innerHTML': 'And then there are those who keep their distance from the technology altogether. This group, which accounts for roughly a tenth of young people, does not see <small>AI</small> as a practical tool. They are anxious about its impact. Their low engagement is more a reflection of their broader societal pessimism than of negative experiences they have had with the technology. We find white and <small>LGBTQ+</small> youth to be overrepresented in this group. For <small>LGBTQ+</small> youth, <small>AI</small> exacerbates their anxiety with surveillance and privacy concerns.'
    },
    {
        'has_initial': False,
        'innerHTML': 'Close to half of young people, however, fall somewhere in between. They engage with <small>AI</small> pragmatically, using it to explore, learn and solve problems, without relying on it for identity or emotional support. Strong social support and a sense of belonging appear to act as buffers, allowing these young people to treat <small>AI</small> as a tool rather than a substitute for connection.'
    },
    {
        'has_initial': False,
        'innerHTML': 'What does this mean for policy and practice? The instinct to regulate access or impose time limits may be misguided. Recent proposals, from school bans on Chat<small>GPT</small> to America's federal <small>GUARD</small> Act, reflect an impulse to reduce exposure as the primary safety mechanism. If <small>AI</small> is functioning as a mobility engine for some young people, a productivity tool for others and an emotional substitute for those lacking support, then exposure alone is the wrong variable to regulate. What's needed is a multi-pronged approach that complements the complex ways in which this technology weaves through young people's lives and, in many ways, mirrors it.'
    },
    {
        'has_initial': False,
        'innerHTML': 'Designing <small>AI</small> systems with strong and smart safety guardrails is essential. Firms have a responsibility to ensure their systems do not expose young users to harmful interactions, and policymakers should hold them accountable. Some governments, such as California's and New York's, are already moving in this direction, with proposals to require clearer disclosures and limit emotionally manipulative design. But product-level fixes alone are insufficient.'
    },
    {
        'has_initial': False,
        'innerHTML': 'The important question is what role the technology ends up playing. Policy should focus on where <small>AI</small> begins to substitute for human support and whether that substitution is safe. That means building paths from <small>AI</small> tools to human care, such as easy connections to mental-health services, and equipping schools and families with the literacy to help youngsters navigate these systems.'
    },
    {
        'has_initial': False,
        'innerHTML': 'Trusted adults are central to this. There is often a disconnect between what parents think their children are using <small>AI</small> for and how they are actually using it. Yet parents and trusted adults remain the most important facilitators of support. Helping them engage in more informed conversations about <small>AI </small>rather than just restricting it will be critical. Expert guidance suggests these conversations should focus on helping teens understand what <small>AI</small> can and cannot do, discussing privacy risks and encouraging critical thinking about <small>AI</small> responses. There are important lessons here from how we failed to equip parents in relation to social-media use.'
    },
    {
        'has_initial': False,
        'innerHTML': 'In short, the debate needs to shift. Instead of asking only how much time the young spend with <small>AI</small>, the question should be about how the technology fits into the social environments shaping their lives. Generative <small>AI</small> will not determine youngsters' well-being on its own. But it may reveal and sometimes amplify the strengths, or the absences, in the human support systems around them. <span class="ufinish">■</span>'
    }
]

# 中文翻译（12 段）
CHINESE_TRANSLATIONS = [
    '传统观点正在迅速形成。社交媒体使用会损害年轻人的心理健康，而生成式人工智能正在侵蚀他们的思考能力。这种焦虑是可以理解的。AI 工具以惊人的速度渗透到青少年的社交生活中，引发了对年龄限制、禁止"AI 伴侣"和更严格监管的呼声。但这场辩论假设 AI 对所有年轻人的影响大致相同，并且经常将使用时长作为风险的主要衡量标准。新兴证据表明情况恰恰相反。同样的技术可以为一些年轻人扩大机会，同时悄然取代其他人的人际支持。',
    '年轻人的社交和情感背景如何影响他们如何使用、何时使用以及为何使用生成式 AI 工具？这对政策制定意味着什么？我所在的健康数据公司团队在 2025 年 11 月对美国 13 至 24 岁年轻人进行了一项大型研究，探讨了这些问题。我们提出了 100 多个关于 AI 使用、对其生活影响以及更广泛的心理健康和生活背景的问题。',
    '我们发现，有些高频 AI 用户蓬勃发展，而有些低频用户却深陷困境。同样的工具根据用户的社会经济背景、触发压力的事件类型以及他们的"人力资本"（即他们拥有的技能和知识）而发挥截然不同的作用。年轻人使用 AI 的方式惊人地不同。',
    '对一些人来说，AI 充当了流动引擎。十分之一的年轻人是乐观的"超级用户"，将生成式 AI 视为学习和机会的工具，用它来构建技能、产生想法和探索新的职业道路。超过三分之二的人表示 AI 为他们开辟了新的机会，超过一半的人表示 AI 给了他们解决问题的信心，对世界更有希望。黑人青年和面临经济困难的人尤其可能属于这一群体，这表明在其他资源稀缺的地方，AI 可以扩大知识和机会的获取。',
    '对规模相似的另一个群体来说，AI 成为了线下缺失的社交和情感支持的替代品。这个令人担忧的群体在感到孤立时会向 AI 寻求对话、情感安慰和建议。这些高频用户报告了更高水平的痛苦，并且不成比例地可能面临欺凌、歧视或经济压力。AI 可能确实比完全没有支持要好。但通用系统并非为安全地扮演这一角色而设计。它们无法可靠地识别何时应该引导年轻人寻求专业帮助。',
    '还有一些人则完全与技术保持距离。这个群体约占年轻人的十分之一，不认为 AI 是实用工具。他们对其影响感到焦虑。他们的低参与度更多反映了他们更广泛的社会悲观情绪，而不是他们对技术的负面体验。我们发现白人和 LGBTQ+ 青年在这个群体中占比过高。对 LGBTQ+ 青年来说，AI 因监控和隐私问题加剧了他们的焦虑。',
    '然而，近一半的年轻人处于两者之间。他们务实地使用 AI，用它来探索、学习和解决问题，而不依赖它来获得身份认同或情感支持。强大的社会支持和归属感似乎起到了缓冲作用，使这些年轻人能够将 AI 视为工具，而不是人际联系的替代品。',
    '这对政策和实践意味着什么？规范访问或实施时间限制的直觉可能是错误的。最近的提议，从学校禁止 ChatGPT 到美国联邦 GUARD 法案，都反映了将减少接触作为主要安全机制的冲动。如果 AI 对一些年轻人来说是流动引擎，对另一些人是生产力工具，对缺乏支持的人是情感替代品，那么仅仅接触就是错误的监管变量。需要的是一种多管齐下的方法，补充这项技术融入年轻人生活的复杂方式，并在许多方面反映它。',
    '设计具有强大智能安全护栏的 AI 系统至关重要。公司有责任确保其系统不会让年轻用户暴露于有害互动，政策制定者应该追究他们的责任。一些政府，如加州和纽约，已经在朝这个方向迈进，提议要求更清晰的披露并限制情感操纵设计。但仅靠产品层面的修复是不够的。',
    '重要的问题是技术最终扮演的角色。政策应该关注 AI 何时开始取代人际支持，以及这种取代是否安全。这意味着建立从 AI 工具到人际关怀的路径，例如与心理健康服务的便捷连接，并为学校和家庭提供素养，帮助他们引导年轻人使用这些系统。',
    '值得信任的成年人是其中的核心。父母认为孩子使用 AI 的目的与实际使用方式之间往往存在脱节。然而，父母和值得信任的成年人仍然是最重要的支持促进者。帮助他们就 AI 进行更知情的对话，而不仅仅是限制，将是关键。专家建议，这些对话应该专注于帮助青少年理解 AI 能做什么和不能做什么，讨论隐私风险，并鼓励对 AI 回复进行批判性思考。从我们在社交媒体使用方面未能装备父母的教训中，我们可以学到重要的经验。',
    '简而言之，辩论需要转变。与其只问年轻人在 AI 上花了多少时间，不如问这项技术如何融入塑造他们生活的社会环境。生成式 AI 本身不会决定年轻人的福祉。但它可能会揭示并有时放大他们周围人际支持系统的优势或缺失。'
]

def convert_small_tags(inner_html):
    """将原文的 <small> 标签转换为微信公众号格式"""
    html = inner_html
    # 移除 <i> 标签（微信不支持）
    html = html.replace('<i>', '').replace('</i>', '')
    # 替换 & 为 &amp;（避免重复转义）
    html = html.replace('&', '&amp;')
    # 将原文的 <small> 标签转换为微信公众号格式
    def replace_small(match):
        content = match.group(1)
        return f'<small style="{SMALL_STYLE}"><span leaf="">{content}</span></small>'
    html = re.sub(r'<small>(.*?)</small>', replace_small, html)
    # 替换结束符号
    html = re.sub(r'<span[^>]*class="ufinish"[^>]*>■</span>', '<span style="color:rgb(227,18,11)">■</span>', html)
    return html

def format_paragraph(inner_html, is_first=False):
    """格式化段落"""
    html = convert_small_tags(inner_html)
    if is_first:
        # 第一段，处理首字母大写
        html = html.replace(
            '<span data-caps="initial">',
            '<span data-caps="initial" style="border:0;font-style:inherit;font-variant:inherit;font-weight:inherit;font-stretch:inherit;line-height:1;font-family:inherit;font-size:3.5rem;margin:0 0.2rem 0 0;padding:0;vertical-align:baseline;float:left;height:3.25rem;text-transform:uppercase;">'
        )
        return f'<p data-component="paragraph" style="border:0;font-style:normal;font-variant:oldstyle-nums;font-weight:400;font-stretch:inherit;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;margin:0;padding:0;color:rgb(13,13,13);text-align:start;"><span leaf="" style="color:rgb(13,13,13);font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;font-style:normal;font-variant-ligatures:normal;font-variant-caps:normal;font-weight:400;letter-spacing:normal;text-align:start;text-indent:0px;text-transform:none;-webkit-text-stroke-width:0px;background-color:rgb(255,255,255);float:none;display:inline!important;">{html}</span></p>'
    else:
        return f'<p data-component="paragraph" style="border:0;font-style:normal;font-variant:oldstyle-nums;font-weight:400;font-stretch:inherit;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;margin:0.875rem 0 0;padding:0;color:rgb(13,13,13);text-align:start;"><span leaf="" style="color:rgb(13,13,13);font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;font-style:normal;font-variant-ligatures:normal;font-variant-caps:normal;font-weight:400;letter-spacing:normal;text-align:start;text-indent:0px;text-transform:none;-webkit-text-stroke-width:0px;background-color:rgb(255,255,255);float:none;display:inline!important;">{html}</span></p>'

def format_chinese_translation(text, is_first=False):
    """格式化中文翻译"""
    margin = "0 0 8px" if is_first else "8px 0 16px"
    return f'<p style="border:0;font-style:normal;font-variant:oldstyle-nums;font-weight:400;font-stretch:inherit;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;margin:{margin};padding:0;color:rgb(13,13,13);text-align:start;"><span leaf="" style="border:0;font-variant-alternates:inherit;font-variant-numeric:inherit;font-variant-east-asian:inherit;font-variant-position:inherit;font-variant-emoji:inherit;font-stretch:inherit;line-height:inherit;font-optical-sizing:inherit;font-size-adjust:inherit;font-kerning:inherit;font-feature-settings:inherit;font-variation-settings:inherit;font-language-override:inherit;margin:0;padding:0;vertical-align:baseline;color:rgb(24,32,38);font-size:14px;" segoe="segoe" ui="ui" sans="sans" neue="neue">{text}</span></p>'

def main():
    # 构建 HTML
    html_parts = [
        '<!DOCTYPE html>',
        '<html>',
        '<head>',
        '  <meta charset="UTF-8">',
        '  <title>经济学人 - How the young use AI matters</title>',
        '</head>',
        '<body>',
        '',
        # 副标题
        '<h1 style="border:0;font-style:normal;font-variant:oldstyle-nums;font-weight:400;font-stretch:inherit;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;margin:0;padding:0;color:rgb(13,13,13);text-align:start;"><span leaf="">That undermines the case for blanket bans or time limits, writes Sema Sgaier</span></h1>',
        '',
        # 副标题中文
        '<p style="border:0;font-style:normal;font-variant:oldstyle-nums;font-weight:400;font-stretch:inherit;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;margin:0 0 8px;padding:0;color:rgb(13,13,13);text-align:start;"><span leaf="" style="border:0;font-variant-alternates:inherit;font-variant-numeric:inherit;font-variant-east-asian:inherit;font-variant-position:inherit;font-variant-emoji:inherit;font-stretch:inherit;line-height:inherit;font-optical-sizing:inherit;font-size-adjust:inherit;font-kerning:inherit;font-feature-settings:inherit;font-variation-settings:inherit;font-language-override:inherit;margin:0;padding:0;vertical-align:baseline;color:rgb(24,32,38);font-size:14px;" segoe="segoe" ui="ui" sans="sans" neue="neue">这削弱了全面禁令或时间限制的合理性</span></p>',
        ''
    ]
    
    # 添加 12 段正文
    for i in range(len(ORIGINAL_PARAGRAPHS)):
        is_first = (i == 0)
        # 英文段落
        html_parts.append(format_paragraph(ORIGINAL_PARAGRAPHS[i]['innerHTML'], is_first))
        # 中文段落
        html_parts.append(format_chinese_translation(CHINESE_TRANSLATIONS[i], is_first))
    
    # 结尾
    html_parts.append('')
    html_parts.append('<p style="display:none;"><mp-style-type data-value="10000"></mp-style-type></p>')
    html_parts.append('</body>')
    html_parts.append('</html>')
    
    content = '\n'.join(html_parts)
    
    # 保存 HTML 文件（UTF-8 无 BOM）
    output_path = TEMP_DIR / 'young_ai_complete.html'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"[OK] HTML 文件已保存：{output_path}")
    print(f"段落数：{len(ORIGINAL_PARAGRAPHS)} 段")

if __name__ == '__main__':
    main()
