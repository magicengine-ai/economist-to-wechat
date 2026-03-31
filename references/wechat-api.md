# 微信公众号 API 参考

## 基础信息

- **AppID**: 公众号唯一标识
- **AppSecret**: 公众号密钥（需保密）
- **API 基础 URL**: `https://api.weixin.qq.com/cgi-bin/`

## 1. 获取 Access Token

**接口**: `GET https://api.weixin.qq.com/cgi-bin/token`

**参数**:
- `grant_type`: `client_credential`
- `appid`: 你的 AppID
- `secret`: 你的 AppSecret

**响应**:
```json
{
  "access_token": "ACCESS_TOKEN",
  "expires_in": 7200
}
```

**注意**: 
- access_token 有效期 2 小时
- 需要缓存复用，不要每次请求都获取
- 每日调用次数有限制

## 2. 上传永久素材（图片）

**接口**: `POST https://api.weixin.qq.com/cgi-bin/material/add_material?access_token=ACCESS_TOKEN&type=IMAGE`

**请求**: multipart/form-data

**参数**:
- `media`: 图片文件（form-data 字段名）
- `type`: `image`

**响应**:
```json
{
  "media_id": "MEDIA_ID",
  "url": "URL",
  "errcode": 0,
  "errmsg": "ok"
}
```

**限制**:
- 图片大小：不超过 2MB
- 格式：JPG, PNG, GIF, BMP
- 永久素材库容量有限

## 3. 新增草稿（图文消息）

**接口**: `POST https://api.weixin.qq.com/cgi-bin/draft/add?access_token=ACCESS_TOKEN`

**请求体**:
```json
{
  "articles": [
    {
      "title": "文章标题",
      "author": "作者",
      "digest": "摘要",
      "content": "<p>正文内容，可包含<img src=\"MEDIA_ID\" />格式的图片</p>",
      "content_source_url": "原文链接",
      "thumb_media_id": "封面图 media_id",
      "show_cover_pic": 1,
      "need_open_comment": 0,
      "only_fans_can_comment": 0
    }
  ]
}
```

**响应**:
```json
{
  "media_id": "DRAFT_MEDIA_ID",
  "errcode": 0,
  "errmsg": "ok"
}
```

## 4. 发布图文消息

**接口**: `POST https://api.weixin.qq.com/cgi-bin/message/mass/sendall?access_token=ACCESS_TOKEN`

**请求体**:
```json
{
  "filter": {
    "is_to_all": true
  },
  "mpnews": {
    "media_id": "DRAFT_MEDIA_ID"
  },
  "msgtype": "mpnews"
}
```

**或使用草稿发布**:
```json
{
  "media_id": "DRAFT_MEDIA_ID"
}
```

## 5. 图片在内容中的使用

在 content 字段中，图片使用以下格式：
```html
<img src=\"MEDIA_ID\" />
```

其中 `MEDIA_ID` 是通过上传素材接口获得的 media_id，不是原始 URL。

## 错误码

- `40001`: 凭证无效
- `42001`: access_token 过期
- `40007`: 素材 ID 无效
- `45001`: 素材大小超限

## Python 示例代码

```python
import requests
import json

# 获取 access_token
def get_token(appid, secret):
    url = "https://api.weixin.qq.com/cgi-bin/token"
    params = {
        "grant_type": "client_credential",
        "appid": appid,
        "secret": secret
    }
    resp = requests.get(url, params=params)
    data = resp.json()
    return data.get("access_token")

# 上传图片
def upload_image(token, image_path):
    url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image"
    with open(image_path, 'rb') as f:
        files = {'media': f}
        resp = requests.post(url, files=files)
    return resp.json()

# 发布文章
def publish_article(token, article_data):
    url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"
    resp = requests.post(url, json=article_data)
    return resp.json()
```
