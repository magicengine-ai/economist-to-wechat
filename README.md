# 经济学人到微信公众号自动发布工具

将经济学人（The Economist）网站文章自动转换为微信公众号格式并发布。

## 功能特性

- ✅ 自动抓取经济学人文章内容和图片
- ✅ 中英文双语对照排版
- ✅ 首字母大写特殊样式（Drop Cap）
- ✅ 自动上传封面图和图表到微信素材库
- ✅ 创建微信公众号草稿
- ✅ 符合经济学人排版规范（字体、字号、间距）
- ✅ 红色■结束符号

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置微信公众号凭证

复制示例文件并填写你的公众号信息：

```bash
cp .wechat-credentials.example.json .wechat-credentials.json
```

编辑 `.wechat-credentials.json`：
```json
{
  "appId": "YOUR_APP_ID",
  "appSecret": "YOUR_APP_SECRET",
  "accountName": "公众号名称"
}
```

### 3. 准备文章内容

编辑 `scripts/economist_to_wechat.py` 中的以下内容：
- `ARTICLE_META`：文章元数据（标题、摘要、来源 URL 等）
- `ENGLISH_PARAGRAPHS`：英文正文段落（7 段）
- `CHINESE_TRANSLATIONS`：中文翻译段落（7 段）

### 4. 下载封面图

```bash
python scripts/download_cover_direct.py
```

### 5. 下载图表（可选）

如果文章包含图表，编辑 `scripts/download_chart_direct.py` 中的图表 URL，然后运行：

```bash
python scripts/download_chart_direct.py
```

### 6. 发布到微信公众号

```bash
python scripts/economist_to_wechat.py
```

### 7. 在公众号后台检查

1. 登录 https://mp.weixin.qq.com
2. 在「草稿箱」中找到文章
3. 预览效果，确认无误后发布

## 文件结构

```
economist-to-wechat/
├── SKILL.md                          # 技能文档（完整使用说明）
├── requirements.txt                  # Python 依赖
├── .wechat-credentials.example.json  # 微信凭证示例
├── .gitignore                        # Git 忽略文件
├── references/                       # 参考资料
│   ├── format-template.html         # HTML 格式模板
│   └── wechat-api.md                # 微信 API 文档
└── scripts/                          # Python 脚本
    ├── economist_to_wechat.py       # 主发布脚本
    ├── download_cover_direct.py     # 下载封面图
    ├── download_chart_direct.py     # 下载图表
    ├── test_preview.py              # 生成 HTML 预览
    ├── deepl_translate.py           # DeepL 自动翻译
    └── ...                          # 其他辅助脚本
```

## 标题格式

微信公众号标题格式：**经济学人 | 中文标题 | 英文标题**

- 微信限制标题长度为 64 字符
- 如果超长，自动去掉"经济学人 | "前缀
- 如果还超长，截断英文部分
- 示例：`经济学人 | 市场陷入令人担忧的认知失调 | Markets are gripped by an a...`

## 格式规范

### 文章结构

1. 副标题（英文）`<h1>`
2. 副标题（中文）`<p>` + `<span>`
3. 主图 `<section>`
4. 正文段落 1（英文 + 中文）- 带首字母大写
5. 正文段落 2（英文 + 中文）
6. 正文段落 3（英文 + 中文）
7. 图表 `<section>`（居中，仅一次）
8. 正文段落 4-7（英文 + 中文）
9. 红色■结束符号

### 关键样式

| 元素 | 样式要求 |
|------|---------|
| **英文正文字体** | `font-family: EconomistSerif,ui-serif,Georgia,Times,sans-serif` |
| **英文正文字号** | `font-size: 20px` |
| **英文正文行高** | `line-height: 28px` |
| **中文翻译字号** | `font-size: 14px` |
| **中文翻译颜色** | `color: rgb(24, 32, 38)` |
| **首字母大写** | `font-size: 3.5rem`，`float: left` |
| **结束符号** | 红色 `■`（`color: rgb(227,18,11)`） |

## 常见问题

### Q: 图片上传失败（403 Forbidden）
**原因**: 经济学人图片有 Cloudflare 防盗链保护

**解决方案**: 使用 `download_cover_direct.py` 脚本下载（自动添加 User-Agent 和 Referer）

### Q: 图片上传失败（unsupported file type）
**原因**: 图片实际格式是 WEBP（虽然扩展名是.jpg）

**解决方案**: 脚本已自动转换为 JPG 格式

### Q: 标题太长（title size out of limit）
**原因**: 微信限制标题长度为 64 字符

**解决方案**: 脚本会自动调整标题格式，优先保留中文

### Q: 引号显示异常（有转义字符）
**原因**: Python 字符串中的双引号需要 Unicode 转义

**解决方案**: 
- 英文引号：`"` → `\u201c`，`"` → `\u201d`
- 中文引号：同样使用 Unicode 转义
- 详见 SKILL.md 中的"引号转义问题"章节

### Q: 草稿中有多余的图表
**原因**: `IMAGES_ORDER` 配置了图表，但原文没有图表

**解决方案**:
- 检查原文是否有 `(see chart)` 标记
- 如果没有图表，在 `economist_to_wechat.py` 中只配置封面图
- 详见 SKILL.md 中的"图表处理"章节

### Q: 正文末尾没有结束符号
**原因**: 经济学人文章标准格式要求正文最后有红色 **■** 符号

**解决方案**:
- 检查原文最后一段是否有 **■** 符号
- 在 `ENGLISH_PARAGRAPHS` 和 `CHINESE_TRANSLATIONS` 的最后一段末尾添加
- HTML 代码：`&nbsp;<span style="color:rgb(227,18,11)">■</span>`
- 详见 SKILL.md 中的"结束符号"章节

### Q: 缩写词格式不对（AI、PR 等）
**原因**: 经济学人对缩写词有特殊格式（小写 + small 标签）

**解决方案**:
- 使用 `<small>AI</small>` 格式
- 常见缩写词：AI、PR、STEM、GDP、CEO 等
- 详见 SKILL.md 中的"缩写词格式"章节

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 免责声明

本工具仅供学习和个人使用。转载经济学人文章可能涉及版权保护，请确保你有合法的使用权限。商业用途请联系 The Economist Group 获取授权。
