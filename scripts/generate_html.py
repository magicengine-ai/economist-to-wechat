# -*- coding: utf-8 -*-
"""生成 HTML 预览文件"""

import sys
from pathlib import Path

sys.path.insert(0, 'scripts')
from economist_to_wechat import *

# 构建文章内容
content_html = build_article_content([], None)

# 保存为 HTML 文件
html_file = WORKSPACE / 'temp' / 'wechat_output' / 'china_ai_talent.html'
html_file.parent.mkdir(parents=True, exist_ok=True)

with open(html_file, 'w', encoding='utf-8') as f:
    f.write('<!DOCTYPE html>\n')
    f.write('<html>\n')
    f.write('<head>\n')
    f.write('  <meta charset="UTF-8">\n')
    f.write('  <title>经济学人 - 中国正在赢得 AI 人才竞赛</title>\n')
    f.write('</head>\n')
    f.write('<body>\n')
    f.write(content_html)
    f.write('\n</body>\n')
    f.write('</html>\n')

print(f'HTML 文件已保存到：{html_file}')
print(f'文件大小：{html_file.stat().st_size} bytes')
print(f'文件路径：{html_file.absolute()}')
