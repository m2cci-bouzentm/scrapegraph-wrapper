# ScrapeGraphAI API Wrapper

FastAPI wrapper exposing all 22 ScrapeGraphAI graph types as REST endpoints.

## Endpoints (27 total)

| Category | Endpoint | Graph | Input |
|----------|----------|-------|-------|
| **Core** | POST /scrape | SmartScraperGraph | url, prompt? |
| | POST /extract | SmartScraperGraph | url, prompt |
| | POST /smart-scraper-lite | SmartScraperLiteGraph | url, prompt? |
| | POST /smart-scraper-multi | SmartScraperMultiGraph | urls[], prompt |
| | POST /crawl | SmartScraperMultiConcatGraph | urls[], prompt |
| | POST /smart-scraper-multi-lite | SmartScraperMultiLiteGraph | urls[], prompt |
| **Search** | POST /search | SearchGraph | prompt, max_results? |
| | POST /search-link | SearchLinkGraph | url |
| | POST /omni-search | OmniSearchGraph | prompt, max_results? |
| **Documents** | POST /document-scraper | DocumentScraperGraph | source, prompt |
| | POST /document-scraper-multi | DocumentScraperMultiGraph | sources[], prompt |
| | POST /csv-scraper | CSVScraperGraph | source, prompt |
| | POST /csv-scraper-multi | CSVScraperMultiGraph | sources[], prompt |
| | POST /json-scraper | JSONScraperGraph | source, prompt |
| | POST /json-scraper-multi | JSONScraperMultiGraph | sources[], prompt |
| | POST /xml-scraper | XMLScraperGraph | source, prompt |
| | POST /xml-scraper-multi | XMLScraperMultiGraph | sources[], prompt |
| **Visual** | POST /omni-scraper | OmniScraperGraph | url, prompt |
| | POST /screenshot-scraper | ScreenshotScraperGraph | url, prompt |
| **Deep** | POST /depth-search | DepthSearchGraph | url, prompt |
| **Code** | POST /script-creator | ScriptCreatorGraph | url, prompt |
| | POST /script-creator-multi | ScriptCreatorMultiGraph | urls[], prompt |
| | POST /code-generator | CodeGeneratorGraph | url, prompt |
| **Speech** | POST /speech | SpeechGraph | url, prompt |
| **Monitor** | POST /monitor | SmartScraperGraph | url, prompt |
| | GET /monitors/{domain} | — | — |
| **Health** | GET /health | — | — |

## Setup

```bash
cp .env.example .env
# Edit .env with your API keys
docker compose up -d
```

## Auth

All endpoints (except /health, /docs, /openapi.json) require `X-API-KEY` header.

```bash
curl -X POST http://localhost:8091/extract \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: your_api_key" \
  -d '{"url": "https://example.com", "prompt": "Extract main content"}'
```
