---
name: economist-to-wechat
description: 将经济学人网站文章转换为微信公众号格式并发布。支持：1) 浏览器抓取 innerHTML（保留 initial/small 标签）2) 根据原文 initial 标签判断首字母大写 3) 转换原文 small 标签为微信格式 4) 上传图片到微信素材库 5) 创建草稿。Use when user wants to: (1) Fetch article innerHTML from Economist.com (preserving initial/small tags), (2) Apply initial capital format based on original initial tags, (3) Convert original small tags to WeChat format, (4) Upload images and create drafts.
---

# 经济学人到微信公众号转换技能

## 快速开始

### 一键发布（推荐）✨

```bash
# 从 URL 直接发布（自动完成所有步骤）
cd economist-to-wechat
python scripts/publish_from_url.py https://www.economist.com/leaders/2026/04/01/...
```

**自动完成：**
1. ✅ 浏览器抓取原文 innerHTML（保留 initial/small 标签）
2. ✅ 下载封面图
3. ✅ 发布前检查（检测英文中的中文字符）
4. ✅ 翻译（DeepL 自动翻译或手动编辑）
5. ✅ 转换格式（small 标签、首字母大写）
6. ✅ 上传封面图
7. ✅ 创建草稿
8. ✅ 清理临时文件

**配置：**
- 微信公众号凭证：`~/.openclaw/workspace/.wechat-credentials.json`
- DeepL 凭证（可选）：`~/.openclaw/workspace/.deepl-credentials.json`

---

### 分步执行（高级）

```bash
# 1. 抓取文章（手动在浏览器执行 JavaScript）
# 2. 准备数据文件（article-data.json）
# 3. 发布
python scripts/economist_to_wechat.py article-data.json
```

---

### 完整工作流程（手动模式）

#### 步骤 1：使用浏览器抓取原文（⚠️ 关键）

**⚠️ 必须抓取 innerHTML，不能用 textContent！**

经济学人网站使用 `<body-text class="svelte-qapeiq">` 标签分段，需要通过浏览器工具抓取：

```javascript
// ✅ 正确：抓取 innerHTML（保留 HTML 标签）
const article = document.querySelector('article');
const paragraphs = Array.from(article.querySelectorAll('p')).map((p, i) => {
  const innerHTML = p.innerHTML;  // ← 关键：用 innerHTML 而非 textContent
  const hasInitial = p.querySelector('span[data-caps="initial"]') !== null;
  const text = innerHTML.trim();
  return text.length > 50 ? { innerHTML: text, has_initial: hasInitial } : null;
}).filter(x => x !== null);
```

```javascript
// ❌ 错误：抓取 textContent（丢失标签）
const paragraphs = Array.from(article.querySelectorAll('p')).map(p => p.textContent.trim());
// 问题：会丢失 <span data-caps="initial"> 和 <small> 标签
```

**关键规则：**
- ✅ **抓取 innerHTML**：保留 `<span data-caps="initial">` 和 `<small>` 标签
- ✅ **首字母大写**：只有原文有 `<span data-caps="initial">` 标签的段落才使用首字母大写格式
- ✅ **small 标签**：直接使用原文的 `<small>` 标签位置，不自动检测
- ✅ **副标题**：从原文 `<h2>` 标签获取，不要自己编
- ✅ **结束符号**：原文正文最后一段末尾有 `■` 符号（红色）要保留，中文翻译后也要加上
- ✅ **段落数量**：只发布正文段落，**不包含作者介绍段落**
- ✅ **作者介绍**：原文最后一段通常是作者介绍（如"Ethan Mollick is..."），这部分**不应该发布**

#### 步骤 2：获取副标题和封面图片

**副标题（⚠️ 必须从原文获取）：**
```javascript
// 获取原文副标题
const subtitle = document.querySelector('article h2')?.textContent.trim();
// 示例："Ahead of an election due in October, a divided opposition and the war could hand him a lifeline"
```

**⚠️ 不要自己编副标题！** 必须使用原文的副标题。

**封面图片（防盗链处理）：**
```bash
# 设置图片 URL（从文章页面获取）
# 运行下载脚本（自动转换为 JPG 格式）
python economist-to-wechat/scripts/download_cover_direct.py
```

**方法 B：浏览器截图**
1. 用浏览器打开文章页面
2. 用 JavaScript 获取图片 URL：`() => document.querySelector('article img').src`
3. 在新 tab 中打开图片链接
4. 截图保存
5. 裁剪并调整尺寸为 900x383（可选）

**正文配图（可选）：**
```javascript
// 获取文章所有配图
const images = Array.from(document.querySelectorAll('article img[src*="cdn-cgi"]'))
  .map(img => ({ src: img.src, alt: img.alt || '' }));
```

经济学人文章通常包含多张配图，发布时应该：
1. 下载所有配图（浏览器截图方式，绕过防盗链）
2. 上传到微信素材库
3. 在对应段落之间插入图片

#### 步骤 3：配置微信公众号凭证
在 workspace 根目录创建 `.wechat-credentials.json`：
```json
{
  "appId": "YOUR_APP_ID",
  "appSecret": "YOUR_APP_SECRET",
  "accountName": "公众号名称"
}
```

#### 步骤 4：发布到微信公众号
```bash
python economist-to-wechat/scripts/economist_to_wechat.py
```

#### 步骤 5：在公众号后台检查
1. 登录 https://mp.weixin.qq.com
2. 在「草稿箱」中找到文章
3. 预览效果，确认无误后发布

---

## ⚠️ 关键注意事项（必读）

### 1. 抓取原文必须用 innerHTML

**❌ 错误做法：**
```javascript
p.textContent  // 丢失所有 HTML 标签
```

**✅ 正确做法：**
```javascript
p.innerHTML  // 保留 <span data-caps="initial"> 和 <small> 标签
```

**后果：** 如果用 textContent，首字母大写格式和 small 标签格式都会丢失！

---

### 2. 副标题必须从原文获取

**❌ 错误做法：** 自己编一个中文副标题

**✅ 正确做法：**
```javascript
const subtitle = document.querySelector('article h2')?.textContent.trim();
```

**原文示例：**
> Ahead of an election due in October, a divided opposition and the war could hand him a lifeline

---

### 3. 中文翻译末尾必须加结束符号

**❌ 错误做法：** 中文翻译最后没有 ■

**✅ 正确做法：**
```json
{
  "chinese": [
    "...而不是内塔尼亚胡先生的利益。<span class=\"ufinish\">■</span>"
  ]
}
```

**原因：** 原文最后一段有 `<span class="ufinish">■</span>`，中文翻译后也要保持一致。

---

### 4. 正文配图处理

经济学人文章通常包含多张配图，发布时应该：
1. 抓取所有配图 URL
2. 用浏览器截图方式下载（绕过防盗链）
3. 上传到微信素材库
4. 在对应段落之间插入

**获取配图代码：**
```javascript
const images = Array.from(document.querySelectorAll('article img[src*="cdn-cgi"]'))
  .map(img => ({ src: img.src, alt: img.alt || '' }));
```

---

### 5. 通用技能原则

**本技能是通用工具，不应该：**
- ❌ 包含特定文章的硬编码数据
- ❌ 包含特定文章的脚本（如 convert_young_ai.py）
- ❌ 提交临时文件到 Git

**特定文章的处理方式：**
1. 在临时目录创建发布脚本
2. 发布完成后删除临时文件
3. 只保留通用核心代码

---

## 缩写词转换规则

### 功能说明

**检测原文的 `<small>` 标签**，转换为**带完整样式的 `<small>` 标签**（添加样式 + `<span leaf="">` 包裹），保持经济学人的标准排版格式。

**不是从纯文本自动检测**，而是：
1. 从原文提取 innerHTML（保留原文 small 标签的位置）
2. 检测到原文有 `<small>AI</small>` 标签
3. 转换为微信公众号格式：`<small style="完整样式"><span leaf="">AI</span></small>`

### 原文中的缩写词示例

经济学人原文中，缩写词已经用 `<small>` 标签包裹：
```html
Until recently, most leading <small>AI</small> research was produced by experts...
...Conference on Neural Information Processing Systems (Neur<small>IPS</small>)...
...<small>MIT</small>, the leading American institution...
...(<small>STEM</small>): around two-fifths...
```

### 转换规则

**将原文的 `<small>` 标签**，添加完整样式和 `<span leaf="">` 包裹：

```python
# 原文（从浏览器抓取）
<small>AI</small>

# 转换后（微信公众号）
<small style="border:0;font-style:inherit;font-variant-ligatures:none;font-variant-caps:small-caps;font-variant-numeric:normal;font-variant-east-asian:normal;font-variant-alternates:normal;font-variant-position:normal;font-variant-emoji:normal;font-weight:inherit;font-stretch:inherit;line-height:inherit;font-family:inherit;font-size:inherit;margin:0;padding:0;vertical-align:baseline;display:inline;text-transform:lowercase;">
  <span leaf="">AI</span>
</small>
```

### Python 实现

```python
import re

# small 标签样式
SMALL_STYLE = 'border:0;font-style:inherit;...;text-transform:lowercase;'

def convert_small_tags(inner_html):
    """将原文的 <small> 标签转换为微信公众号格式"""
    html = inner_html
    
    # 替换 <small> 标签
    def replace_small(match):
        content = match.group(1)
        return f'<small style="{SMALL_STYLE}"><span leaf="">{content}</span></small>'
    
    html = re.sub(r'<small>(.*?)</small>', replace_small, html)
    
    return html
```

### 转换示例

**原文（经济学人网站）：**
```html
<small>AI</small> research is advancing rapidly.
The <small>IPO</small> was successful.
<small>S</small>&amp;<small>P</small> 500 reached a new high.
```

**转换后（微信公众号）：**
```html
<small style="完整样式"><span leaf="">AI</span></small> research is advancing rapidly.
The <small style="完整样式"><span leaf="">IPO</span></small> was successful.
<small style="完整样式"><span leaf="">S</span></small>&<small style="完整样式"><span leaf="">P</span></small> 500 reached a new high.
```

---

## 首字母大写格式

### 判断规则

**只有原文有 `<span data-caps="initial">` 标签的段落才使用首字母大写格式。**

**原文示例：**
```html
<body-text class="svelte-qapeiq">
  <span data-caps="initial">I</span><small>s IT POSSIBLE</small> that the United States...
</body-text>
```

**提取纯文本：**
```
Is IT POSSIBLE that the United States...
```

**转换后：**
```html
<p data-component="paragraph" style="...">
  <span data-caps="initial" style="font-size:3.5rem;float:left;height:3.25rem;text-transform:uppercase;">
    <span leaf="">I</span>
  </span>
  <small style="完整样式"><span leaf="">s IT POSSIBLE</span></small>
  <span leaf="">&nbsp;that the United States...</span>
</p>
```

**关键：**
- ✅ 不自己查找首字母
- ✅ 根据原文的 `data-caps="initial"` 标签判断
- ✅ 只有第 1 段通常有 initial 标签

---

## 段落结构

### 原文分段标签

经济学人使用 `<body-text class="svelte-qapeiq">` 标签分段：

```html
<body-text class="svelte-qapeiq">副标题</body-text>
<body-text class="svelte-qapeiq"><span data-caps="initial">I</span><small>s IT POSSIBLE</small>...</body-text>
<body-text class="svelte-qapeiq">Until recently, most leading AI research...</body-text>
...
```

### 转换后段落

**副标题（第 1 段）：**
```html
<h1 style="..."><span leaf="">Its lead over the West is only set to widen</span></h1>
```

**正文第 1 段（带首字母）：**
```html
<p data-component="paragraph" style="...">
  <span data-caps="initial" style="...">I</span>
  <small style="...">s IT POSSIBLE</small>
  ...
</p>
```

**正文其他段落：**
```html
<p data-component="paragraph" style="...">
  Until recently, most leading <small style="..."><span leaf="">AI</span></small> research...
</p>
```

### 段落数量

- **副标题**：1 段
- **正文**：根据原文 body-text 标签数量（通常 15-20 段）
- **中文翻译**：每段英文后添加对应的中文翻译

---

## 格式规范

### 文章结构

```
1. 副标题（英文）<h1>
2. 副标题（中文）<p> + <span>
3. 主图 <section>（可选）
4. 正文段落 1（英文 + 中文）- 带首字母大写（如原文有 initial 标签）
5. 正文段落 2（英文 + 中文）
6. 正文段落 3（英文 + 中文）
7. 图表 <section>（居中，仅一次，如原文有图表）
8. 正文段落 4-N（英文 + 中文）
9. 结束符号 ■（红色，最后一段末尾）
```

### HTML 格式模板

#### 1. 副标题（英文）
```html
<h1 style="border:0;font-style:normal;font-variant:oldstyle-nums;font-weight:400;font-stretch:inherit;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;margin:0;padding:0;color:rgb(13,13,13);text-align:start;">
  <span leaf="">Its lead over the West is only set to widen</span>
</h1>
```

#### 2. 副标题（中文）
```html
<p style="border:0;font-style:normal;font-variant:oldstyle-nums;font-weight:400;font-stretch:inherit;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;margin:0 0 8px;padding:0;color:rgb(13,13,13);text-align:start;">
  <span leaf="" style="border:0;font-variant-alternates:inherit;font-variant-numeric:inherit;font-variant-east-asian:inherit;font-variant-position:inherit;font-variant-emoji:inherit;font-stretch:inherit;line-height:inherit;font-optical-sizing:inherit;font-size-adjust:inherit;font-kerning:inherit;font-feature-settings:inherit;font-variation-settings:inherit;font-language-override:inherit;margin:0;padding:0;vertical-align:baseline;color:rgb(24,32,38);font-size:14px;" segoe="segoe" ui="ui" sans="sans" neue="neue">
    其对西方的领先优势只会不断扩大
  </span>
</p>
```

#### 3. 正文第一段（带首字母大写，如原文有 initial 标签）
```html
<p data-component="paragraph" style="border:0;font-style:normal;font-variant:oldstyle-nums;font-weight:400;font-stretch:inherit;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;margin:0;padding:0;color:rgb(13,13,13);text-align:start;">
  <span data-caps="initial" style="border:0;font-style:inherit;font-variant:inherit;font-weight:inherit;font-stretch:inherit;line-height:1;font-family:inherit;font-size:3.5rem;margin:0 0.2rem 0 0;padding:0;vertical-align:baseline;float:left;height:3.25rem;text-transform:uppercase;">
    <span leaf="">I</span>
  </span>
  <small style="border:0;font-style:inherit;font-variant-ligatures:none;font-variant-caps:small-caps;font-variant-numeric:normal;font-variant-east-asian:normal;font-variant-alternates:normal;font-variant-position:normal;font-variant-emoji:normal;font-weight:inherit;font-stretch:inherit;line-height:inherit;font-family:inherit;font-size:inherit;margin:0;padding:0;vertical-align:baseline;display:inline;text-transform:lowercase;">
    <span leaf="">s IT POSSIBLE</span>
  </small>
  <span leaf="">&nbsp;that the United States falls behind China?...</span>
</p>
```

#### 4. 正文其他段落（普通格式，缩写词自动检测）
```html
<p data-component="paragraph" style="border:0;font-style:normal;font-variant:oldstyle-nums;font-weight:400;font-stretch:inherit;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;margin:0.875rem 0 0;padding:0;color:rgb(13,13,13);text-align:start;">
  <span leaf="" style="color:rgb(13,13,13);font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;font-style:normal;font-variant-ligatures:normal;font-variant-caps:normal;font-weight:400;letter-spacing:normal;text-align:start;text-indent:0px;text-transform:none;-webkit-text-stroke-width:0px;background-color:rgb(255,255,255);float:none;display:inline!important;">
    Until recently, most leading <small style="完整样式"><span leaf="">AI</span></small> research was produced by experts based in the West...
  </span>
</p>
```

#### 5. 中文段落
```html
<p style="border:0;font-style:normal;font-variant:oldstyle-nums;font-weight:400;font-stretch:inherit;line-height:28px;font-family:EconomistSerif,ui-serif,Georgia,Times,sans-serif;font-size:20px;margin:8px 0 16px;padding:0;color:rgb(13,13,13);text-align:start;">
  <span leaf="" style="border:0;font-variant-alternates:inherit;font-variant-numeric:inherit;font-variant-east-asian:inherit;font-variant-position:inherit;font-variant-emoji:inherit;font-stretch:inherit;line-height:inherit;font-optical-sizing:inherit;font-size-adjust:inherit;font-kerning:inherit;font-feature-settings:inherit;font-variation-settings:inherit;font-language-override:inherit;margin:0;padding:0;vertical-align:baseline;color:rgb(24,32,38);font-size:14px;" segoe="segoe" ui="ui" sans="sans" neue="neue">
    直到最近，大多数领先的 AI 研究仍由西方专家完成...
  </span>
</p>
```

#### 6. 结束符号（最后一段末尾）
```html
<span style="color:rgb(227,18,11)">■</span>
```

### 关键样式规则

| 元素 | 样式要求 |
|------|---------|
| **英文正文字体** | `font-family: EconomistSerif,ui-serif,Georgia,Times,sans-serif` |
| **英文正文字号** | `font-size: 20px` |
| **英文正文行高** | `line-height: 28px` |
| **英文正文颜色** | `color: rgb(13, 13, 13)` |
| **英文段落间距** | 第一段 `margin: 0`，其他段 `margin: 0.875rem 0 0` |
| **中文翻译字号** | `font-size: 14px` |
| **中文翻译颜色** | `color: rgb(24, 32, 38)` |
| **中文段落间距** | `margin: 8px 0 16px`（顶部 8px，底部 16px） |
| **首字母大写** | `font-size: 3.5rem`，`float: left`，`height: 3.25rem`（仅当原文有 initial 标签） |
| **第一个单词小大写** | `<small>` 标签，`font-variant-caps: small-caps`（仅当原文有 initial 标签） |
| **中文 span 属性** | 必须添加 `segoe="segoe" ui="ui" sans="sans" neue="neue"` |
| **缩写词 small** | 自动检测缩写词，添加完整样式 + `<span leaf="">` 包裹 |
| **结束符号** | 红色 `color: rgb(227,18,11)` |

### 重要注意事项

1. **分段规则**：使用原文的 `<body-text>` 标签，不要手动分段
2. **首字母大写**：只有原文有 `<span data-caps="initial">` 标签的段落才使用首字母大写格式
3. **缩写词**：检测原文的 `<small>` 标签，转换为微信公众号格式（**不使用纯文本自动检测**）
4. **中文翻译**：必须用 `<span leaf="">` 包裹，添加 segoe/ui/sans/neue 属性
5. **中文 span 不指定 font-family**，继承父元素样式
6. **标题长度限制**：微信公众号限制标题长度，控制在 50 字符以内
7. **结束符号**：最后一段英文和中文末尾都必须添加红色 `■` 符号（红色样式：`color:rgb(227,18,11)`）
8. **图表处理**：如原文有图表，插入在第 3 段后，居中显示（仅一次）
9. **段落数量**：**只发布正文段落，不包含作者介绍**
   - 经济学人 By Invitation 栏目文章最后通常有作者介绍段落（如"Ethan Mollick is..."）
   - 这部分**不应该包含在发布内容中**
   - 正文最后一段末尾已有 `■` 符号，作者介绍段不需要
10. **临时文件清理**：发布脚本和数据文件用完即删，不要留在 temp 目录

---

## 微信公众号 API

### 获取 Access Token
```
GET https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=APPID&secret=APPSECRET
```

### 上传图片素材
```
POST https://api.weixin.qq.com/cgi-bin/material/add_material?access_token=ACCESS_TOKEN&type=image
Content-Type: multipart/form-data
```

### 创建草稿
```
POST https://api.weixin.qq.com/cgi-bin/draft/add?access_token=ACCESS_TOKEN
Content-Type: application/json

{
  "articles": [{
    "title": "标题",
    "author": "作者",
    "digest": "摘要",
    "content": "HTML 内容",
    "content_source_url": "原文链接",
    "thumb_media_id": "封面图 media_id",
    "show_cover_pic": 1
  }]
}
```

## 配置

### 微信公众号凭证

在 workspace 根目录创建 `.wechat-credentials.json`：

```json
{
  "appId": "YOUR_APP_ID",
  "appSecret": "YOUR_APP_SECRET",
  "accountName": "公众号名称"
}
```

**注意**: 
- 将此文件加入 `.gitignore`，不要提交到版本控制
- **凭证只需配置一次**，后续会自动读取使用
- 不要每次都询问用户，应该主动从配置文件读取

### DeepL API 凭证（可选）

使用一键发布时，如有 DeepL 凭证会自动翻译：

在 workspace 根目录创建 `.deepl-credentials.json`：

```json
{
  "api_key": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx:fx",
  "api_url": "https://api-free.deepl.com/v2/translate"
}
```

**获取方法：**
1. 访问 https://www.deepl.com/pro-api 注册账号
2. 选择 DeepL API Free（免费套餐，每月 500,000 字符）
3. 在 Account → API 页面复制 API Key

**注意**: 
- 免费套餐足够翻译经济学人文章（每月约 20-30 篇）
- 如无 DeepL 凭证，一键发布会提示手动翻译

### DeepL API 凭证（可选）

在 workspace 根目录创建 `.deepl-credentials.json`：

```json
{
  "api_key": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx:fx",
  "api_url": "https://api-free.deepl.com/v2/translate"
}
```

**注意**: 
- 免费套餐每月 500,000 字符，足够翻译经济学人文章
- 同样加入 `.gitignore`，不要提交

## 发布前检查清单

一键发布工具会自动执行以下检查：

### 自动检查项目

1. **英文段落中的中文字符**
   - 检测：`re.search(r'[\u4e00-\u9fff]', html)`
   - 原因：手动简化英文段落时误输入中文
   - 解决：使用原始 innerHTML，不手动修改

2. **small 标签匹配**
   - 检测：`<small>` 和 `</small>` 数量是否相等
   - 原因：标签未闭合会导致格式错误
   - 解决：从浏览器重新抓取该段落

3. **initial 标签验证**
   - 检测：标记为 `has_initial: true` 的段落是否包含 `<span data-caps="initial">`
   - 原因：标签丢失会导致首字母大写格式失效
   - 解决：检查浏览器抓取代码

### 手动检查项目

- [ ] 副标题是否从原文 `<h2>` 获取（非自己编造）
- [ ] 段落数量是否正确（排除作者介绍）
- [ ] 最后一段是否有红色 ■ 结束符号
- [ ] 中文翻译是否流畅准确
- [ ] 封面图是否清晰（建议 900x383 或 1280x720）

---

## 常见问题

### Q: 英文段落中出现中文字符
**原因**: 手动简化英文段落时误输入中文

**解决方案**:
1. **使用原始 innerHTML** - 直接使用浏览器抓取的完整英文段落，不手动修改
2. **发布前检查** - 运行自动检查脚本检测中文字符
```python
import re
for i, para in enumerate(PARAGRAPHS):
    if re.search(r'[\u4e00-\u9fff]', para['innerHTML']):
        print(f"⚠️ 警告：第{i+1}段英文中包含中文字符")
```
3. **修复方法** - 从浏览器重新抓取该段落的 innerHTML

### Q: 中文显示为 `\uXXXX` 或乱码
**原因**: Python 的 `json.dumps()` 默认会将非 ASCII 字符转义为 `\uXXXX` 格式

**解决方案**: 
```python
# ❌ 错误：中文会被转义为 \uXXXX
requests.post(url, json={'articles': articles})

# ✅ 正确：使用 json.dumps 并设置 ensure_ascii=False
data = json.dumps({'articles': articles}, ensure_ascii=False)
requests.post(url, data=data, headers={'Content-Type': 'application/json; charset=utf-8'})
```

**关键点**:
1. 使用 `json.dumps(..., ensure_ascii=False)` 手动序列化
2. 设置 `Content-Type: application/json; charset=utf-8`
3. 使用 `data` 参数而非 `json` 参数发送请求

---

### Q: 图片上传失败（403 Forbidden）
**原因**: 经济学人图片有 Cloudflare 防盗链保护

**解决方案**:
1. 使用 `download_cover_direct.py` 脚本下载（自动添加 User-Agent 和 Referer）
2. 或通过浏览器打开图片链接后截图
3. 确保图片转换为 JPG 格式（微信不支持 WEBP）

### Q: 图片上传失败（unsupported file type）
**原因**: 图片实际格式是 WEBP（虽然扩展名是.jpg）

**解决方案**: 使用 PIL 转换为真正的 JPG 格式：
```python
from PIL import Image
img = Image.open('image.jpg')
if img.mode in ('RGBA', 'LA', 'P'):
    img = img.convert('RGB')
img.save('output.jpg', 'JPEG', quality=95)
```

### Q: 标题太长（title size out of limit）
**原因**: 微信限制标题长度为 50 字符

**解决方案**: 
- 使用格式：`经济学人｜中文标题｜英文标题`
- 脚本会自动截断超长部分
- 建议控制在 20 字以内

### Q: 摘要太长（description size out of limit）
**原因**: 微信限制摘要长度为 120 字符

**解决方案**: 
- 摘要控制在 50 字以内
- 使用简洁的描述，如"伊朗石油收入是战前两倍"

### Q: 封面图不显示
**原因**: 
1. 图片尺寸不合适（推荐 900x383 或 1280x720）
2. 图片格式不支持（必须为 JPG）
3. 图片上传失败

**解决方案**:
- 检查图片尺寸和格式
- 确认上传成功（脚本输出 "[OK] 图片 X 上传成功"）

### Q: 中文翻译最后没有结束符号■
**原因**: 原文最后一段有 `<span class="ufinish">■</span>`，但中文翻译需要手动添加

**解决方案**:
```python
# 最后一段中文翻译必须加■（红色样式）
CHINESE_TRANSLATIONS = [
    "...",
    "这种极端的冗余引入了如此复杂的层次...否则它不会被扼制。<span style=\"color:rgb(227,18,11)\">■</span>"  # ← 加红色■
]
```

**注意**:
- ■符号必须是**红色**（原文样式）
- 红色样式：`<span style="color:rgb(227,18,11)">■</span>`
- 只在正文最后一段添加，作者介绍段不需要
```

### Q: 英文段落中的链接被过滤
**原因**: 微信公众号不支持正文中的 `<a>` 链接标签

**解决方案**:
- 脚本会自动移除 `<a>` 标签，保留文本
- 如需添加链接，可在文章末尾统一添加"阅读原文"链接

### Q: 格式标签（small/initial）不生效
**原因**: 标签缺少完整的内联样式

**解决方案**:
- 确保 `<small>` 标签包含完整样式并使用 `<span leaf="">` 包裹
- 确保 `<span data-caps="initial">` 包含正确的样式定义
- 使用脚本自动转换，不要手动编辑 HTML

### Q: 段落数量不对/包含了作者介绍
**原因**: 经济学人 By Invitation 栏目文章最后通常有作者介绍段落

**解决方案**:
- **只发布正文段落**，不包含作者介绍
- 正文最后一段末尾已有 `■` 符号
- 作者介绍段格式如："Ethan Mollick is an associate professor at..."
- 判断方法：正文结束后，下一段通常是作者介绍，应该排除

### Q: DeepL API 如何配置
**原因**: 使用 DeepL 自动翻译需要 API Key

**解决方案**:
1. 访问 https://www.deepl.com/pro-api 注册账号
2. 选择 DeepL API Free（免费套餐，每月 500,000 字符）
3. 在 Account → API 页面复制 API Key
4. 在 workspace 根目录创建 `.deepl-credentials.json`：
```json
{
  "api_key": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx:fx",
  "api_url": "https://api-free.deepl.com/v2/translate"
}
```
5. 或设置环境变量：`$env:DEEPL_API_KEY="your-api-key"`

## 最佳实践

### 中文编码（⚠️ 关键）

**问题**: Python 的 `json.dumps()` 默认会将中文转义为 `\uXXXX`

**正确做法**:
```python
# ✅ 创建草稿时
data = json.dumps({'articles': articles}, ensure_ascii=False)
response = requests.post(url, data=data, headers={'Content-Type': 'application/json; charset=utf-8'})
```

**关键点**:
1. 使用 `json.dumps(..., ensure_ascii=False)` 手动序列化
2. 设置 `Content-Type: application/json; charset=utf-8`
3. 使用 `data` 参数而非 `json` 参数发送请求

### 图片处理
- **推荐尺寸**: 900x383（微信封面图标准）或 1280x720（高清）
- **推荐格式**: JPEG，质量 90-95
- **文件大小**: < 2MB（微信限制）

### 内容格式
- **正文段落**: 根据原文 body-text 标签数量（通常 15-20 段）
- **首字母大写**: 第一段英文首字母特殊样式（如原文有 initial 标签）
- **结束符号**: 最后一段英文和中文末尾添加红色 ■
- **图表**: 第 3 段后插入，居中显示（仅一次）
- **缩写词**: 检测原文的 `<small>` 标签，转换为微信公众号格式

### 临时文件清理（⚠️ 重要）

**原则**：临时脚本和数据文件用完即删

**正确做法**:
```bash
# 发布完成后删除临时文件
rm temp/publish-xxx.py
rm temp/xxx-article-translated.json
```

**理由**:
- 保持 workspace 整洁
- 避免混淆不同文章的数据
- 符合通用技能原则（不包含特定文章数据）

### 英文段落处理（⚠️ 关键）

**规则 1：使用完整 innerHTML**
```
✅ 正确：使用浏览器抓取的完整 innerHTML（包含所有 HTML 标签）
❌ 错误：手动简化、删除标签或修改内容
```

**理由：**
- 原文的 `<small>`、`<span data-caps="initial">` 等标签需要被脚本转换
- 手动简化会丢失标签，导致格式错误或混入其他语言字符

**示例：**
```python
# ✅ 正确：完整的 innerHTML（包含 small 标签）
{"innerHTML": "Most...going to the Islamic Revolutionary Guard Corps (<small>IRGC</small>)...", "has_initial": False}

# ❌ 错误：手动简化后丢失 small 标签，可能混入中文
{"innerHTML": "Most...going to the IRGC...", "has_initial": False}
```

**规则 2：发布前自动检查**
```python
# 检测英文段落中的中文字符
import re
for i, para in enumerate(PARAGRAPHS):
    if re.search(r'[\u4e00-\u9fff]', para['innerHTML']):
        print(f"⚠️ 警告：第{i+1}段英文中包含中文字符")

# 检查是否有未转换的标签
def check_tags(inner_html):
    issues = []
    if '<i>' in inner_html or '</i>' in inner_html:
        issues.append("包含不支持的<i>标签")
    if '<a ' in inner_html:
        issues.append("包含链接标签（微信会过滤）")
    if '<small>' in inner_html and 'style=' not in inner_html:
        issues.append("small 标签缺少样式")
    return issues
```

**规则 3：标签转换规则**
微信公众号对 HTML 标签有严格限制：

| 标签 | 微信支持 | 处理方式 |
|------|---------|---------|
| `<span>` | ✅ 支持 | 必须添加内联样式 |
| `<small>` | ✅ 支持 | 转换为带完整样式的格式 + `<span leaf="">` 包裹 |
| `<p>` | ✅ 支持 | 基础段落标签 |
| `<h1>`-`<h6>` | ✅ 支持 | 标题标签 |
| `<img>` | ✅ 支持 | 图片标签 |
| `<a>` | ❌ 不支持 | 移除标签，保留文本 |
| `<i>` | ❌ 不支持 | 移除标签 |
| `data-*` 属性 | ⚠️ 可能被过滤 | 保留但可能无效 |

**转换示例：**
```python
# 移除 <i> 标签
html = html.replace('<i>', '').replace('</i>', '')

# 移除链接标签，保留文本
html = re.sub(r'<a[^>]*>(.*?)</a>', r'\1', html)

# 转换 <small> 标签（添加完整样式）
<small>AI</small> → <small style="完整样式"><span leaf="">AI</span></small>

# 转换 initial span（首字母大写）
<span data-caps="initial">F</span> → <span data-caps="initial" style="完整样式">F</span>
```

### 标题和摘要

**标题格式（⚠️ 重要）：**
```
经济学人｜中文标题｜英文原标题
```

**示例：**
```
经济学人｜伊朗的能源战争｜How Iran is making a mint from Trump's war
```

**长度限制：**
- **标题**: 微信限制 64 字，建议总长控制在 128 字符以内
  - "经济学人｜" 固定 5 字
  - 中文标题建议 10-15 字
  - 英文原标题如超长可截断或省略
- **摘要**: 控制在 50 字以内（微信限制 120 字符）

### 中文翻译
- **每段对照**: 每段英文后紧跟对应的中文翻译
- **最后一段**: 必须添加红色 ■ 结束符号
- **格式**: 使用 14px 字号，灰色字体 (rgb(24,32,38))

### 发布流程（完整清单）

1. **浏览器抓取原文**
   - 打开经济学人文章页面
   - 使用 JavaScript 抓取 innerHTML（保留 initial/small 标签）
   - 确认段落数量（正文 + 作者介绍）

2. **获取副标题**
   - 从原文 `<h2>` 标签获取（不要自己编）

3. **下载封面图**
   - 使用 `download_cover_direct.py` 或浏览器新 tab 打开链接截图
   - 确认图片格式为 JPG 或 PNG，如果为其他格式需要转换

4. **准备中文翻译**
   - 每段英文对应一段中文
   - 使用 DeepL 或大模型翻译
   - **最后一段正文加红色■**
   - **不包含作者介绍段落**

5. **配置凭证**
   - 微信：`.wechat-credentials.json`（只需配置一次）
   - DeepL：`.deepl-credentials.json`（如使用自动翻译）

6. **发布前检查**
   - 检测英文段落中的中文字符
   - 检查标签转换（small/initial）
   - 确认段落数量正确

7. **上传图片**
   - 上传封面图到微信素材库（永久素材）
   - 保存 media_id

8. **构建 HTML**
   - 转换 small 标签为微信格式
   - 处理首字母大写样式
   - 添加中英文对照

9. **创建草稿**
   - ⚠️ 使用 `json.dumps(..., ensure_ascii=False)`
   - 设置 `Content-Type: application/json; charset=utf-8`

10. **公众号后台检查**
    - 登录 https://mp.weixin.qq.com
    - 在「草稿箱」中找到文章
    - 预览效果，确认排版无误

11. **清理临时文件**
    - 删除临时脚本和数据文件
    - 保持 workspace 整洁

12. **发布**
    - 确认无误后群发或定时发布

## 使用示例

### 示例 1：一键发布（推荐）

```bash
cd economist-to-wechat

# 从 URL 直接发布
python scripts/publish_from_url.py https://www.economist.com/leaders/2026/04/01/lessons-for-the-world-from-tiny-hungary
```

**执行流程：**
```
[1/9] 正在抓取文章内容...
  打开：https://www.economist.com/...
  ✓ 标题：Lessons for the world from tiny Hungary
  ✓ 副标题：A regime loved by MAGA may soon lose power
  ✓ 段落数：10
  ✓ 封面图：https://www.economist.com/cdn-cgi/image/...

[2/9] 正在下载封面图...
  ✓ 已保存：.../hungary_cover.jpg
  ✓ 大小：95,512 bytes

[3/9] 原始数据已备份：.../article_backup_xxx.json

[4/9] 发布前检查...
  ✓ 检查通过

[5/9] 正在使用 DeepL 翻译...
  ✓ 段落 1: 256 → 180 字
  ✓ 段落 2: 312 → 220 字
  ...

[6/9] 正在获取 access token...
  ✓ Token 获取成功

[7/9] 正在上传封面图...
  ✓ 上传成功：JLQIpNSBY2BaUZxD9-7ew...

[8/9] 正在创建草稿：经济学人｜来自小国匈牙利的世界启示｜Lessons...
  ✓ 草稿创建成功

[9/9] 清理临时文件...

============================================================
✓ 发布完成！
============================================================
标题：经济学人｜来自小国匈牙利的世界启示｜Lessons from tiny Hungary
段落：10 段
翻译：10 段

请登录 https://mp.weixin.qq.com 查看草稿箱
```

### 示例 2：仅下载封面图
```bash
python economist-to-wechat/scripts/economist_to_wechat.py https://www.economist.com/business/2026/03/29/the-plan-to-make-ipos-great-again
```

### 示例 2：下载文章图片
```bash
python economist-to-wechat/scripts/download_images.py https://www.economist.com/business/2026/03/26/...
```

### 示例 3：单独获取访问令牌
```bash
python economist-to-wechat/scripts/get_wechat_token.py
```

### 示例 4：单独上传图片
```bash
python economist-to-wechat/scripts/upload_image.py /path/to/image.jpg
```

## 故障排除

### 问题：中文显示乱码
**原因**: 使用了错误的字体或编码
**解决**: 确保中文 span 使用正确的样式，不指定 font-family，添加 segoe/ui/sans/neue 属性

### 问题：标题太长
**原因**: 微信公众号限制标题长度
**解决**: 缩短英文标题，使用 `标题中文 | 标题英文` 格式

### 问题：图片上传失败
**原因**: 图片超过 2MB 或格式不支持
**解决**: 压缩图片到 2MB 以内，使用 JPG/PNG 格式

### 问题：音频无法上传
**原因**: 经济学人音频有防盗链保护
**解决**: 跳过音频，或提供原文链接

## 参考文件

- [微信 API 参考](references/wechat-api.md)
- [格式模板](references/format-template.html)
- [示例脚本](scripts/economist_to_wechat.py)
