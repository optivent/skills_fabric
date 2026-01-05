import asyncio
from crawl4ai import AsyncWebCrawler

async def crawl_batch(urls, prefix):
    async with AsyncWebCrawler() as crawler:
        for i, url in enumerate(urls):
            print(f'Crawling {url}...')
            result = await crawler.arun(url=url)
            if result.success:
                filename = f'/home/aig/{prefix}_{i}.md'
                with open(filename, 'w') as f:
                    f.write(result.markdown)
                print(f'Saved to {filename}')
            else:
                print(f'Failed {url}: {result.error_message}')

async def main():
    opencode_urls = [
        'https://opencode.ai/docs/skills/',
        'https://opencode.ai/docs/plugins/',
        'https://opencode.ai/docs/tools/',
        'https://opencode.ai/docs/mcp-servers/',
        'https://opencode.ai/docs/acp/',
        'https://opencode.ai/docs/custom-tools/'
    ]
    # For Claude Plugins, I want to see the specific plugins listed on the page
    claude_urls = [
        'https://github.com/anthropics/claude-code/tree/main/plugins'
    ]
    
    await crawl_batch(opencode_urls, 'opencode_docs_sub')
    await crawl_batch(claude_urls, 'claude_plugins_list')

if __name__ == "__main__":
    asyncio.run(main())
