# 自由哔站

> 🎬 **自由哔站** 是一个高性能、使用方便的影视聚合搜索和播放工具。它基于 **Python Fastapi** + **Vue.js** 构建，亮点是支持并行搜索视频，基于SSE低延迟响应查询结果，带来极致流畅的体验。

![Next.js](https://img.shields.io/badge/Python-13-green?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![Docker Ready](https://img.shields.io/badge/Docker-ready-blue?logo=docker)

## ✨ 功能特性
- **多源并行搜索**：支持多资源站点并行搜索
- **SSE流式接口**：流式API接口，解决资源站点API有的响应时间长，有的响应时间短，时间短响应的接口会立刻返回
- **多源分辨率自动排序**: 自动获取各源的第一个视频的分比率，将高分辨率排在前面
- **聚合功能**: 将相同 douban id 的视频聚合到一块，页面更加清爽易用
- **支持hash链接直接跳转到视频**: 支持链接一键直达视频，在搜索和播放的时候自动更改页面url
- **记住上次播放的集数和视频源**：会记住上次播放的集数和视频源，下次打开自动跳转
- **网页标题显示为当前播放和搜索的视频**：搜索和播放视频会更改网页标题，方便将链接放到网页收藏夹
- **极简部署**：一条 Docker 命令即可启动项目

## 页面展示
![开始界面1](docs/1.png)
![开始界面2](docs/2.png)
![开始界面3](docs/3.png)

## Docker 部署 (推荐)
```
docker run -d -p 8000:8000 silvery886/freebili:1.24
```

## 开发启动
```
# 本项目使用uv管理python依赖
uv sync
# 启动项目
uv run fastapi dev main.py
```
## 配置文件
访问 ``ip + /docs`` 页面，``post /config``接口，上传 config.json
![配置界面](docs/api.png)

## json配置文件参考如下
```
{
    "site_name": "自由哔站",
    "pc_background_image_url": "https://www.loliapi.com/acg/pc/",
    "phone_background_image_url": "https://www.loliapi.com/acg/pe/",
    "timeout": 5,
    "base_urls": [
        {
            "name": "资源站点1",
            "base_url": "http://example.com/api.php/provide/vod"
        },
    ]
}
```
**site_name** : 网站名称

**pc_background_image_url** : 电脑端背景图片

**phone_background_image_url** : 手机端背景图片

**timeout** ： 并行接口超时时间，单位秒，超过这个时间对应资源站API会被跳过

**base_url** : http://example.com/api.php/provide/vod 注意vod后不要加/