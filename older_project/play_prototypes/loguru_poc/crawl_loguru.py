import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig

async def main():
    browser_config = BrowserConfig(headless=True)
    run_config = CrawlerRunConfig()
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        # Using the correct CodeWiki pattern found in codewiki_robust.py
        result = await crawler.arun(
            url='https://codewiki.google/github.com/Delgan/loguru',
            config=run_config
        )
        if result.success:
            with open('loguru_docs.md', 'w') as f:
                f.write(result.markdown)
            print('Successfully crawled Loguru docs')
        else:
            print(f'Failed to crawl: {result.error_message}')

if __name__ == '__main__':
    asyncio.run(main())
