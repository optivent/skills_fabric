import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig

async def main():
    url = "https://codewiki.google/github.com/Delgan/loguru"
    
    # Hardened config for potential network flakiness
    browser_config = BrowserConfig(headless=True)
    run_config = CrawlerRunConfig(
        wait_until="load", # Less aggressive than networkidle
        delay_before_return_html=5.0,
    )
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url, config=run_config)
        if result.success:
            with open("loguru_raw_crawl.md", "w", encoding="utf-8") as f:
                f.write(result.markdown)
            print(f"SUCCESS: Crawled {len(result.markdown)} characters.")
        else:
            print(f"FAILED: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(main())
