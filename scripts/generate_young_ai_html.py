# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
转换 JSON 数据为微信公众号 HTML 格式
"""

import json
import re
from pathlib import Path

WORKSPACE = Path.home() / '.openclaw' / 'workspace'
TEMP_DIR = WORKSPACE / 'temp' / 'wechat_output'

SMALL_STYLE = 'border:0;font-style:inherit;font-variant-ligatures:none;font-variant-caps:small-caps;font-variant-numeric:normal;font-variant-east-asian:normal;font-variant-alternates:normal;font-variant-position:normal;font-variant-emoji:normal;font-weight:inherit;font-stretch:inherit;line-height:inherit;font-family:inherit;font-size:inherit;margin:0;padding:0;vertical-align:baseline;display:inline;text-transform:lowercase;'

def convert_small_tags(inner_html):
    html = inner_html
    html = html.replace('<i>', '').replace('</i>', '')
    html = html.replace('&', '&amp;')
    def replace_small(match):
        content = match.group(1)
        return f'<small style="{SMALL_STYLE}"><span leaf="">{content}</span></small>'
    html = re.sub(r'<small>(.*?)</small>', replace_small, html)
    html = re.sub(r'<span[^>]*class="ufinish"[^>]*>■</span>', '<span style="color:rgb(227,18,11)">■</span>', html)
    return html

def format_paragraph(inner_html, is_first=False):
    html = convert_small_tags(inner_html)
    if is_first:
        html = html.replace(
            '<span data-caps="initial">',
            '<span data-caps="initial" style="border:0;font-style:inherit;font-variant:inherit;font-weight:inherit;font-stretch:inherit;line-height:1;font-family:inherit;font-size:3.5rem;margin:0 0.2rem 0 0;padding:0;vertical-align:baseline;float:left;height:3.25rem;text-transform:uppercase;">'
        )
        return f'<p data-component="paragraph" style="border:0;font-style:normal;font-variant:oldstyle-nums;font-weight:400;font-stretch:inherit;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;margin:0;padding:0;color:rgb(13,13,13);text-align:start;"><span leaf="" style="color:rgb(13,13,13);font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;font-style:normal;font-variant-ligatures:normal;font-variant-caps:normal;font-weight:400;letter-spacing:normal;text-align:start;text-indent:0px;text-transform:none;-webkit-text-stroke-width:0px;background-color:rgb(255,255,255);float:none;display:inline!important;">{html}</span></p>'
    else:
        return f'<p data-component="paragraph" style="border:0;font-style:normal;font-variant:oldstyle-nums;font-weight:400;font-stretch:inherit;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;margin:0.875rem 0 0;padding:0;color:rgb(13,13,13);text-align:start;"><span leaf="" style="color:rgb(13,13,13);font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;font-style:normal;font-variant-ligatures:normal;font-variant-caps:normal;font-weight:400;letter-spacing:normal;text-align:start;text-indent:0px;text-transform:none;-webkit-text-stroke-width:0px;background-color:rgb(255,255,255);float:none;display:inline!important;">{html}</span></p>'

def format_chinese(text, is_first=False):
    margin = "0 0 8px" if is_first else "8px 0 16px"
    return f'<p style="border:0;font-style:normal;font-variant:oldstyle-nums;font-weight:400;font-stretch:inherit;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;margin:{margin};padding:0;color:rgb(13,13,13);text-align:start;"><span leaf="" style="border:0;font-variant-alternates:inherit;font-variant-numeric:inherit;font-variant-east-asian:inherit;font-variant-position:inherit;font-variant-emoji:inherit;font-stretch:inherit;line-height:inherit;font-optical-sizing:inherit;font-size-adjust:inherit;font-kerning:inherit;font-feature-settings:inherit;font-variation-settings:inherit;font-language-override:inherit;margin:0;padding:0;vertical-align:baseline;color:rgb(24,32,38);font-size:14px;" segoe="segoe" ui="ui" sans="sans" neue="neue">{text}</span></p>'

def main():
    # 读取 JSON 数据
    with open(WORKSPACE / 'economist-to-wechat' / 'scripts' / 'young_ai_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    paragraphs = data['paragraphs']
    chinese = data['chinese']
    
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
        '<h1 style="border:0;font-style:normal;font-variant:oldstyle-nums;font-weight:400;font-stretch:inherit;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;margin:0;padding:0;color:rgb(13,13,13);text-align:start;"><span leaf="">That undermines the case for blanket bans or time limits, writes Sema Sgaier</span></h1>',
        '',
        '<p style="border:0;font-style:normal;font-variant:oldstyle-nums;font-weight:400;font-stretch:inherit;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;margin:0 0 8px;padding:0;color:rgb(13,13,13);text-align:start;"><span leaf="" style="border:0;font-variant-alternates:inherit;font-variant-numeric:inherit;font-variant-east-asian:inherit;font-variant-position:inherit;font-variant-emoji:inherit;font-stretch:inherit;line-height:inherit;font-optical-sizing:inherit;font-size-adjust:inherit;font-kerning:inherit;font-feature-settings:inherit;font-variation-settings:inherit;font-language-override:inherit;margin:0;padding:0;vertical-align:baseline;color:rgb(24,32,38);font-size:14px;" segoe="segoe" ui="ui" sans="sans" neue="neue">这削弱了全面禁令或时间限制的合理性</span></p>',
        ''
    ]
    
    for i in range(len(paragraphs)):
        is_first = (i == 0)
        html_parts.append(format_paragraph(paragraphs[i]['innerHTML'], is_first))
        html_parts.append(format_chinese(chinese[i], is_first))
    
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
    print(f"段落数：{len(paragraphs)} 段")
    print(f"文件大小：{len(content)} 字节")

if __name__ == '__main__':
    main()
