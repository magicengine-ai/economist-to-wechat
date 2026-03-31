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

### 3. 使用浏览器抓取文章

**⚠️ 关键：必须抓取 innerHTML，不能用 textContent！**

```javascript
// 打开经济学人文章页面，在控制台运行
const article = document.querySelector('article');
const paragraphs = Array.from(article.querySelectorAll('p')).map((p, i) => {
  const innerHTML = p.innerHTML;  // ← 关键：用 innerHTML
  const hasInitial = p.querySelector('span[data-caps="initial"]') !== null;
  const text = innerHTML.trim();
  return text.length > 50 ? { innerHTML: text, has_initial: hasInitial } : null;
}).filter(x => x !== null);

// 获取副标题
const subtitle = document.querySelector('article h2')?.textContent.trim();

// 获取配图
const images = Array.from(document.querySelectorAll('article img[src*="cdn-cgi"]'))
  .map(img => ({ src: img.src, alt: img.alt || '' }));
```

### 4. 下载封面图

```bash
python scripts/download_cover_direct.py <图片 URL> <输出路径>
```

**或用浏览器截图方式（绕过防盗链）：**
1. 新标签页打开图片 URL
2. 浏览器截图保存

### 5. 发布到微信公众号

```bash
python scripts/economist_to_wechat.py
```

### 6. 在公众号后台检查

1. 登录 https://mp.weixin.qq.com
2. 在「草稿箱」中找到文章
3. 预览效果，确认无误后发布

## 文件结构

```
economist-to-wechat/
├── SKILL.md                          # 技能文档（完整使用说明）
├── README.md                         # 本文件
├── requirements.txt                  # Python 依赖
├── .wechat-credentials.example.json  # 微信凭证示例
├── .gitignore                        # Git 忽略文件
├── references/                       # 参考资料
│   ├── format-template.html         # HTML 格式模板
│   └── wechat-api.md                # 微信 API 文档
└── scripts/                          # Python 脚本
    ├── economist_to_wechat.py       # 主发布脚本
    ├── convert_11paras.py           # 11 段格式转换
    ├── economist_to_wechat_deepl.py # DeepL 自动翻译
    ├── download_cover_direct.py     # 下载封面图
    ├── download_chart_direct.py     # 下载图表
    ├── download_images.py           # 下载图片
    ├── download_cover.py            # 下载封面（备用）
    ├── extract_cover_from_screenshot.py # 从截图提取封面
    ├── get_wechat_token.py          # 获取微信 token
    └── upload_image.py              # 上传图片
```

## ⚠️ 注意事项

### 关键要点

1. **抓取 innerHTML**：必须用 `p.innerHTML` 而非 `p.textContent`，否则丢失格式标签
2. **副标题从原文获取**：不要自己编，用 `document.querySelector('article h2')`
3. **中文末尾加■**：最后一段中文翻译后加 `<span class="ufinish">■</span>`
4. **配图下载**：用浏览器截图方式绕过防盗链
5. **通用技能**：不包含特定文章数据，临时脚本用完即删

### 常见错误

| 错误 | 后果 | 正确做法 |
|------|------|----------|
| 用 textContent 抓取 | 丢失首字母大写和 small 标签 | 用 innerHTML |
| 自己编副标题 | 与原文不符 | 从原文 h2 标签获取 |
| 中文不加■ | 格式不完整 | 最后一段加 `<span class="ufinish">■</span>` |
| 直接下载图片 | 403 Forbidden | 浏览器截图 |

---

## 工作流程

```
1. 浏览器抓取文章 → 2. 下载封面图 → 3. 转换格式 → 4. 上传图片 → 5. 创建草稿
```

## 注意事项

- ⚠️ **不要修改核心脚本**：每次新文章应该创建临时脚本，用完即删
- ⚠️ **敏感凭证**：`.wechat-credentials.json` 不要提交到 Git
- ⚠️ **临时文件**：`temp/` 目录内容不提交

## 详细文档

- **完整使用说明**：查看 `SKILL.md`
- **音频功能**：查看 `README_AUDIO.md`
- **配置说明**：查看 `配置说明.md`

## 许可证

MIT License
