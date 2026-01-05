import asyncio
import sys
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig

async def main():
    url = "https://codewiki.google/github.com/Delgan/loguru"
    
    browser_config = BrowserConfig(headless=True)
    run_config = CrawlerRunConfig(
        wait_until="networkidle",
        delay_before_return_html=30.0, # 30s to be safe
        js_code="window.scrollTo(0, document.body.scrollHeight);",
    )
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url, config=run_config)
        if result.success:
            with open("loguru_raw_unmodified.md", "w", encoding="utf-8") as f:
                f.write(result.markdown)
            print(f"SUCCESS: {len(result.markdown)} characters captured.")
        else:
            print(f"ERROR: {result.error_message}", file=sys.stderr)

if __name__ == "__main__":
    asyncio.run(main())
