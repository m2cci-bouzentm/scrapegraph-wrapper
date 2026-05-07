"""
ScrapeGraphAI FastAPI wrapper — all 22 graph types.
"""

import os
import json
import base64
import tempfile
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
load_dotenv()

_executor = ThreadPoolExecutor(max_workers=4)

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel

from scrapegraphai.graphs import (
    SmartScraperGraph,
    SmartScraperLiteGraph,
    SmartScraperMultiGraph,
    SmartScraperMultiConcatGraph,
    SmartScraperMultiLiteGraph,
    SearchGraph,
    SearchLinkGraph,
    OmniSearchGraph,
    DocumentScraperGraph,
    DocumentScraperMultiGraph,
    CSVScraperGraph,
    CSVScraperMultiGraph,
    JSONScraperGraph,
    JSONScraperMultiGraph,
    XMLScraperGraph,
    XMLScraperMultiGraph,
    OmniScraperGraph,
    ScreenshotScraperGraph,
    DepthSearchGraph,
    ScriptCreatorGraph,
    ScriptCreatorMultiGraph,
    CodeGeneratorGraph,
    SpeechGraph,
)

app = FastAPI(title="ScrapeGraphAI API", version="2.0.0")

API_KEY = os.getenv("API_KEY", "")
MONITOR_DIR = Path(os.getenv("MONITOR_DIR", "/data/monitors"))
MONITOR_DIR.mkdir(parents=True, exist_ok=True)


def get_graph_config(max_results: Optional[int] = None) -> dict:
    config = {
        "llm": {
            "api_key": os.getenv("GOOGLE_API_KEY"),
            "model": os.getenv("LLM_MODEL", "google_genai/gemini-2.0-flash"),
        },
        "verbose": False,
        "headless": True,
    }
    if max_results:
        config["max_results"] = max_results
    return config


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if request.url.path in ("/health", "/docs", "/openapi.json"):
        return await call_next(request)
    key = request.headers.get("X-API-KEY", "")
    if not API_KEY or key != API_KEY:
        return JSONResponse(status_code=401, content={"detail": "Invalid or missing API key"})
    return await call_next(request)


@app.get("/health")
async def health():
    return {"status": "ok", "version": "2.0.0", "endpoints": 27}


async def run_graph(graph):
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(_executor, graph.run)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Core Scrapers ────────────────────────────────────────────────

class ScrapeRequest(BaseModel):
    url: str
    prompt: Optional[str] = "Convert this entire page content to well-structured Markdown. Preserve headings, lists, links, and formatting."

class ExtractRequest(BaseModel):
    url: str
    prompt: str

class MultiUrlRequest(BaseModel):
    urls: List[str]
    prompt: str

class LiteRequest(BaseModel):
    url: str
    prompt: Optional[str] = ""


@app.post("/scrape")
async def scrape(req: ScrapeRequest):
    graph = SmartScraperGraph(prompt=req.prompt, source=req.url, config=get_graph_config())
    return await run_graph(graph)


@app.post("/extract")
async def extract(req: ExtractRequest):
    graph = SmartScraperGraph(prompt=req.prompt, source=req.url, config=get_graph_config())
    return await run_graph(graph)


@app.post("/smart-scraper-lite")
async def smart_scraper_lite(req: LiteRequest):
    graph = SmartScraperLiteGraph(source=req.url, config=get_graph_config(), prompt=req.prompt)
    return await run_graph(graph)


@app.post("/smart-scraper-multi")
async def smart_scraper_multi(req: MultiUrlRequest):
    graph = SmartScraperMultiGraph(prompt=req.prompt, source=req.urls, config=get_graph_config())
    return await run_graph(graph)


@app.post("/crawl")
async def crawl(req: MultiUrlRequest):
    graph = SmartScraperMultiConcatGraph(prompt=req.prompt, source=req.urls, config=get_graph_config())
    return await run_graph(graph)


@app.post("/smart-scraper-multi-lite")
async def smart_scraper_multi_lite(req: MultiUrlRequest):
    graph = SmartScraperMultiLiteGraph(prompt=req.prompt, source=req.urls, config=get_graph_config())
    return await run_graph(graph)


# ── Search ───────────────────────────────────────────────────────

class SearchRequest(BaseModel):
    prompt: str
    max_results: Optional[int] = 5

class SearchLinkRequest(BaseModel):
    url: str


@app.post("/search")
async def search(req: SearchRequest):
    graph = SearchGraph(prompt=req.prompt, config=get_graph_config(max_results=req.max_results))
    return await run_graph(graph)


@app.post("/search-link")
async def search_link(req: SearchLinkRequest):
    graph = SearchLinkGraph(source=req.url, config=get_graph_config())
    return await run_graph(graph)


@app.post("/omni-search")
async def omni_search(req: SearchRequest):
    graph = OmniSearchGraph(prompt=req.prompt, config=get_graph_config(max_results=req.max_results))
    return await run_graph(graph)


# ── Document / File Scrapers ─────────────────────────────────────

class DocumentRequest(BaseModel):
    prompt: str
    source: str

class DocumentMultiRequest(BaseModel):
    prompt: str
    sources: List[str]


@app.post("/document-scraper")
async def document_scraper(req: DocumentRequest):
    graph = DocumentScraperGraph(prompt=req.prompt, source=req.source, config=get_graph_config())
    return await run_graph(graph)


@app.post("/document-scraper-multi")
async def document_scraper_multi(req: DocumentMultiRequest):
    graph = DocumentScraperMultiGraph(prompt=req.prompt, source=req.sources, config=get_graph_config())
    return await run_graph(graph)


@app.post("/csv-scraper")
async def csv_scraper(req: DocumentRequest):
    graph = CSVScraperGraph(prompt=req.prompt, source=req.source, config=get_graph_config())
    return await run_graph(graph)


@app.post("/csv-scraper-multi")
async def csv_scraper_multi(req: DocumentMultiRequest):
    graph = CSVScraperMultiGraph(prompt=req.prompt, source=req.sources, config=get_graph_config())
    return await run_graph(graph)


@app.post("/json-scraper")
async def json_scraper(req: DocumentRequest):
    graph = JSONScraperGraph(prompt=req.prompt, source=req.source, config=get_graph_config())
    return await run_graph(graph)


@app.post("/json-scraper-multi")
async def json_scraper_multi(req: DocumentMultiRequest):
    graph = JSONScraperMultiGraph(prompt=req.prompt, source=req.sources, config=get_graph_config())
    return await run_graph(graph)


@app.post("/xml-scraper")
async def xml_scraper(req: DocumentRequest):
    graph = XMLScraperGraph(prompt=req.prompt, source=req.source, config=get_graph_config())
    return await run_graph(graph)


@app.post("/xml-scraper-multi")
async def xml_scraper_multi(req: DocumentMultiRequest):
    graph = XMLScraperMultiGraph(prompt=req.prompt, source=req.sources, config=get_graph_config())
    return await run_graph(graph)


# ── Visual Scrapers ──────────────────────────────────────────────

@app.post("/omni-scraper")
async def omni_scraper(req: ExtractRequest):
    graph = OmniScraperGraph(prompt=req.prompt, source=req.url, config=get_graph_config())
    return await run_graph(graph)


@app.post("/screenshot-scraper")
async def screenshot_scraper(req: ExtractRequest):
    graph = ScreenshotScraperGraph(prompt=req.prompt, source=req.url, config=get_graph_config())
    return await run_graph(graph)


# ── Deep Crawl ───────────────────────────────────────────────────

@app.post("/depth-search")
async def depth_search(req: ExtractRequest):
    graph = DepthSearchGraph(prompt=req.prompt, source=req.url, config=get_graph_config())
    return await run_graph(graph)


# ── Code Generation ──────────────────────────────────────────────

class ScriptRequest(BaseModel):
    url: str
    prompt: str

class ScriptMultiRequest(BaseModel):
    urls: List[str]
    prompt: str


@app.post("/script-creator")
async def script_creator(req: ScriptRequest):
    graph = ScriptCreatorGraph(prompt=req.prompt, source=req.url, config=get_graph_config())
    return await run_graph(graph)


@app.post("/script-creator-multi")
async def script_creator_multi(req: ScriptMultiRequest):
    graph = ScriptCreatorMultiGraph(prompt=req.prompt, source=req.urls, config=get_graph_config())
    return await run_graph(graph)


@app.post("/code-generator")
async def code_generator(req: ScriptRequest):
    graph = CodeGeneratorGraph(prompt=req.prompt, source=req.url, config=get_graph_config())
    return await run_graph(graph)


# ── Speech ───────────────────────────────────────────────────────

class SpeechRequest(BaseModel):
    url: str
    prompt: str

@app.post("/speech")
async def speech(req: SpeechRequest):
    config = get_graph_config()
    config["tts_model"] = "tts-1"
    graph = SpeechGraph(prompt=req.prompt, source=req.url, config=config)
    return await run_graph(graph)


# ── Monitor (snapshot + diff) ────────────────────────────────────

class MonitorRequest(BaseModel):
    url: str
    prompt: str


def diff_results(old, new):
    changes = []
    if isinstance(old, dict) and isinstance(new, dict):
        all_keys = set(list(old.keys()) + list(new.keys()))
        for key in all_keys:
            old_val = old.get(key)
            new_val = new.get(key)
            if old_val != new_val:
                changes.append({"field": key, "old": old_val, "new": new_val})
    elif old != new:
        changes.append({"field": "content", "old": old, "new": new})
    return changes


@app.post("/monitor")
async def monitor(req: MonitorRequest):
    graph = SmartScraperGraph(prompt=req.prompt, source=req.url, config=get_graph_config())
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(_executor, graph.run)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    domain = req.url.replace("https://", "").replace("http://", "").split("/")[0].replace(".", "_")
    domain_dir = MONITOR_DIR / domain
    domain_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    snapshot = {
        "url": req.url,
        "prompt": req.prompt,
        "timestamp": datetime.now().isoformat(),
        "data": result,
    }

    snapshot_path = domain_dir / f"{timestamp}.json"
    snapshot_path.write_text(json.dumps(snapshot, indent=2, default=str))

    snapshots = sorted(domain_dir.glob("*.json"))
    changes = []
    if len(snapshots) >= 2:
        prev = json.loads(snapshots[-2].read_text())
        changes = diff_results(prev.get("data", {}), result)

    return {
        "success": True,
        "data": result,
        "snapshot": str(snapshot_path),
        "changes": changes,
        "changes_detected": len(changes) > 0,
    }


@app.get("/monitors/{domain}")
async def list_monitors(domain: str):
    domain_dir = MONITOR_DIR / domain.replace(".", "_")
    if not domain_dir.exists():
        return {"snapshots": []}
    snapshots = sorted(domain_dir.glob("*.json"))
    return {
        "snapshots": [
            json.loads(s.read_text()) for s in snapshots[-10:]
        ]
    }
