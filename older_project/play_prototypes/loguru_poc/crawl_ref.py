import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

async def main():
    browser_conf = BrowserConfig(headless=True)
    run_conf = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        word_count_threshold=10,
        wait_until="networkidle",
        delay_before_return_html=5.0
    )

    # Based on the homepage, these seem to be the key sections
    # I'll crawl the known endpoints found in the homepage scan and common pattern
    urls = [
        "https://docs.ref.tools/getting-started/quick-start",
        "https://docs.ref.tools/getting-started/best-practices",
        # Hypothesized URL structure based on "Tools" section usually present
    ]

    async with AsyncWebCrawler(config=browser_conf) as crawler:
        # First, let's just get the Quick Start and Best Practices to find more links
        for url in urls:
            result = await crawler.arun(
                url=url,
                config=run_conf
            )
            print(f"--- CRAWL: {url} ---")
            print(result.markdown if result.success else f"FAIL: {result.error_message}")
            print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
