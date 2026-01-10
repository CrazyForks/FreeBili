import asyncio
import logfire
import json
from typing import List, Dict, Any
import httpx
from fastapi import FastAPI, Request, HTTPException
from starlette.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from utils import get_config
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

# 获取站点配置
site_config = get_config()

class BaseUrlItem(BaseModel):
    """单个基础URL的数据结构"""
    name: str
    base_url: str

class SiteConfigModel(BaseModel):
    """完整的站点配置数据结构"""
    site_name: str
    pc_background_image_url: str
    phone_background_image_url: str
    timeout: int
    base_urls: List[BaseUrlItem]

# 初始化FastAPI应用
app = FastAPI()
logfire.configure()
logfire.instrument_fastapi(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产请改为具体域名
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载 static 文件夹
app.mount("/static", StaticFiles(directory="static"), name="static")
# 设置模板目录
templates = Jinja2Templates(directory="templates")

def parse_cms_data(source_name: str, cms_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    将从苹果CMS接口获取的原始列表数据解析为需要的格式。
    """
    results = []
    for item in cms_list:
        play_urls_str = item.get("vod_play_url", "").split("$$$")[0]
        
        videos = []
        episodes = play_urls_str.split('#')
        for episode in episodes:
            parts = episode.split('$')
            if len(parts) == 2:
                video_name, video_url = parts
                videos.append({"name": video_name, "video_url": video_url})

        if videos:
            results.append({
                "name": item.get("vod_name", "未知名称"),
                "vod_pic": item.get("vod_pic", ""),
                "videos": videos,
                "vod_id": item.get("vod_id",""),
                "vod_douban_id": item.get("vod_douban_id","")
            })
            
    return {
        "name": source_name,
        "result": results
    }

async def fetch_and_process(client: httpx.AsyncClient, source: Dict[str, str], keyword: str) -> Dict[str, Any] | None:
    """
    异步获取单个API源的数据并进行处理。
    """
    url = f"{source['base_url']}?ac=detail&wd={keyword}"
    name = source['name']
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = await client.get(
            url, 
            timeout=site_config["timeout"], 
            headers=headers, 
            follow_redirects=True
        )
        response.raise_for_status()
        
        data = response.json()
        if data.get("code") == 1 and data.get("list"):
            return parse_cms_data(name, data["list"])
        else:
            return None
            
    except Exception:
        return None

async def search_event_generator(keyword: str, sources: List[Dict[str, str]]):
    """
    用于SSE的异步生成器函数。
    """
    async with httpx.AsyncClient() as client:
        tasks = [
            asyncio.create_task(fetch_and_process(client, source, keyword))
            for source in sources
        ]

        for future in asyncio.as_completed(tasks):
            result = await future
            if result and result.get("result"):
                yield f"data: {json.dumps(result, ensure_ascii=False)}\n\n"

@app.get("/search")
async def search(keyword: str):
    """
    并行搜索接口，使用SSE流式返回结果。
    """
    if not keyword:
        return {"error": "keyword is required"}
        
    return StreamingResponse(
        search_event_generator(keyword, site_config["base_urls"]),
        media_type="text/event-stream"
    )

@app.get("/config")
async def get_site_config():
    return site_config

@app.post("/config")
async def update_config(config_data: SiteConfigModel):
    """
    接收JSON配置，写入本地文件并更新全局变量。
    """
    global site_config

    try:
        config_json_string = config_data.model_dump_json(indent=4)
        file_path = "config.json"
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(config_json_string)

        site_config = config_data.model_dump()

        return {
            "message": "Configuration updated and saved successfully.",
            "current_config": site_config
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error updating config: {e}"
        )

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    渲染并返回 HTML 页面。
    """
    template_variables = {
        "request": request,
        "site_config": site_config
    }
    return templates.TemplateResponse("index.html", template_variables)