# -*- coding: utf-8 -*-
"""
经济学人文章格式转换工具
将原文 innerHTML 转换为微信公众号格式
"""

import re

# small 标签完整样式
SMALL_STYLE = 'border:0;font-style:inherit;font-variant-ligatures:none;font-variant-caps:small-caps;font-variant-numeric:normal;font-variant-east-asian:normal;font-variant-alternates:normal;font-variant-position:normal;font-variant-emoji:normal;font-weight:inherit;font-stretch:inherit;line-height:inherit;font-family:inherit;font-size:inherit;margin:0;padding:0;vertical-align:baseline;display:inline;text-transform:lowercase;'

# initial span 样式
INITIAL_STYLE = 'border:0;font-style:inherit;font-variant:inherit;font-weight:inherit;font-stretch:inherit;line-height:1;font-family:inherit;font-size:3.5rem;margin:0 0.2rem 0 0;padding:0;vertical-align:baseline;float:left;height:3.25rem;text-transform:uppercase;'


def convert_small_tags(inner_html):
    """
    将原文的 <small> 标签转换为微信公众号格式
    
    原文：<small>AI</small>
    转换后：<small style="完整样式"><span leaf="">AI</span></small>
    """
    html = inner_html
    
    # 移除 HTML 注释
    html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
    
    # 移除 <i> 标签（微信不支持）
    html = html.replace('<i>', '').replace('</i>', '')
    
    # 替换 &amp; 为 &（避免重复转义）
    html = html.replace('&amp;', '&')
    
    # 将原文的 <small> 标签转换为微信公众号格式
    def replace_small(match):
        content = match.group(1)
        return f'<small style="{SMALL_STYLE}"><span leaf="">{content}</span></small>'
    
    html = re.sub(r'<small>(.*?)</small>', replace_small, html, flags=re.IGNORECASE)
    
    # 替换结束符号
    html = re.sub(r'<span[^>]*class="ufinish"[^>]*>■</span>', '<span style="color:rgb(227,18,11)">■</span>', html)
    
    return html


def format_first_paragraph(inner_html):
    """
    格式化第一段（带首字母大写）
    
    原文：<span data-caps="initial">I</span><small>s IT POSSIBLE</small>...
    转换后：<span data-caps="initial" style="INITIAL_STYLE"><span leaf="">I</span></span><small style="SMALL_STYLE"><span leaf="">s IT POSSIBLE</span></small>...
    """
    # 先转换 small 标签
    html = convert_small_tags(inner_html)
    
    # 替换 initial span 的样式
    html = html.replace(
        '<span data-caps="initial">',
        f'<span data-caps="initial" style="{INITIAL_STYLE}">'
    )
    
    # 确保 initial span 内的内容也用 <span leaf=""> 包裹
    def wrap_initial_content(match):
        content = match.group(1)
        if not content.startswith('<span leaf="">'):
            return f'<span data-caps="initial" style="{INITIAL_STYLE}"><span leaf="">{content}</span></span>'
        return match.group(0)
    
    html = re.sub(
        r'<span data-caps="initial"[^>]*>([^<]+)</span>',
        wrap_initial_content,
        html
    )
    
    return html


def format_paragraph(inner_html, has_initial=False):
    """
    格式化正文段落
    
    Args:
        inner_html: 原文的 innerHTML
        has_initial: 是否有首字母大写标记
    
    Returns:
        格式化后的 HTML
    """
    if has_initial:
        return format_first_paragraph(inner_html)
    else:
        return convert_small_tags(inner_html)


def format_chinese_paragraph(chinese_text):
    """
    格式化中文段落
    
    Args:
        chinese_text: 中文翻译文本
    
    Returns:
        格式化后的 HTML
    """
    # 处理■符号
    if '■' in chinese_text:
        chinese_text = chinese_text.replace('■', '<span style="color:rgb(227,18,11)">■</span>')
    
    return f'<p style="border:0;font-style:normal;font-variant:oldstyle-nums;font-weight:400;font-stretch:inherit;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;margin:8px 0 16px;padding:0;color:rgb(13,13,13);text-align:start;"><span leaf="" style="border:0;font-variant-alternates:inherit;font-variant-numeric:inherit;font-variant-east-asian:inherit;font-variant-position:inherit;font-variant-emoji:inherit;font-stretch:inherit;line-height:inherit;font-optical-sizing:inherit;font-size-adjust:inherit;font-kerning:inherit;font-feature-settings:inherit;font-variation-settings:inherit;font-language-override:inherit;margin:0;padding:0;vertical-align:baseline;color:rgb(24,32,38);font-size:14px;" segoe="segoe" ui="ui" sans="sans" neue="neue">{chinese_text}</span></p>'


def convert_article(paragraphs, chinese_translations, subtitle=""):
    """
    转换整篇文章
    
    Args:
        paragraphs: 段落列表 [{'innerHTML': str, 'has_initial': bool}, ...]
        chinese_translations: 中文翻译列表
        subtitle: 副标题
    
    Returns:
        完整的 HTML 内容
    """
    html_parts = []
    
    # 副标题（英文）
    if subtitle:
        html_parts.append(f'<h1 style="border:0;font-style:normal;font-variant:oldstyle-nums;font-weight:400;font-stretch:inherit;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;margin:0;padding:0;color:rgb(13,13,13);text-align:start;"><span leaf="">{subtitle}</span></h1>')
    
    for i, para in enumerate(paragraphs):
        inner_html = para.get('innerHTML', '')
        has_initial = para.get('has_initial', False)
        
        # 格式化英文段落
        if i == 0 and has_initial:
            formatted_en = format_first_paragraph(inner_html)
            html_parts.append(f'<p data-component="paragraph" style="border:0;font-style:normal;font-variant:oldstyle-nums;font-weight:400;font-stretch:inherit;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;margin:0;padding:0;color:rgb(13,13,13);text-align:start;">{formatted_en}</p>')
        else:
            formatted_en = convert_small_tags(inner_html)
            margin = "0.875rem 0 0" if i > 0 else "0"
            html_parts.append(f'<p data-component="paragraph" style="border:0;font-style:normal;font-variant:oldstyle-nums;font-weight:400;font-stretch:inherit;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;margin:{margin};padding:0;color:rgb(13,13,13);text-align:start;"><span leaf="">{formatted_en}</span></p>')
        
        # 添加中文翻译
        if i < len(chinese_translations) and chinese_translations[i]:
            html_parts.append(format_chinese_paragraph(chinese_translations[i]))
    
    return '\n'.join(html_parts)
