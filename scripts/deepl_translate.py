# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
DeepL 翻译模块
"""

import requests
import os
from pathlib import Path

# DeepL API 配置
DEEPL_API_KEY = os.getenv('DEEPL_API_KEY', '')
DEEPL_API_URL = "https://api-free.deepl.com/v2/translate"


def translate_text(text, target_lang='ZH'):
    """
    使用 DeepL 翻译文本
    
    Args:
        text: 要翻译的英文文本
        target_lang: 目标语言（默认 ZH=中文）
    
    Returns:
        翻译后的文本
    """
    if not DEEPL_API_KEY:
        raise Exception("未设置 DeepL API 密钥，请设置环境变量 DEEPL_API_KEY")
    
    headers = {
        'Authorization': f'DeepL-Auth-Key {DEEPL_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'text': [text],
        'target_lang': target_lang,
        'source_lang': 'EN'
    }
    
    response = requests.post(DEEPL_API_URL, headers=headers, json=payload, timeout=30)
    result = response.json()
    
    if 'translations' not in result:
        raise Exception(f"DeepL 翻译失败：{result}")
    
    return result['translations'][0]['text']


def translate_paragraphs(paragraphs):
    """
    批量翻译段落
    
    Args:
        paragraphs: 英文段落列表
    
    Returns:
        中文段落列表
    """
    translations = []
    for i, para in enumerate(paragraphs, 1):
        print(f"[INFO] 翻译段落 {i}/{len(paragraphs)}...")
        try:
            translation = translate_text(para)
            translations.append(translation)
            print(f"[OK] 翻译完成")
        except Exception as e:
            print(f"[WARN] 翻译失败：{e}")
            # 翻译失败时返回原文
            translations.append(para)
    
    return translations


def main():
    """测试翻译功能"""
    test_text = "For many businesses, a jump in fuel prices is a one-two punch."
    
    print(f"[INFO] 测试翻译：{test_text}")
    try:
        result = translate_text(test_text)
        print(f"[OK] 翻译结果：{result}")
    except Exception as e:
        print(f"[ERROR] {e}")


if __name__ == '__main__':
    main()
