import asyncio
from crawl4ai import AsyncWebCrawler

async def test_crawl4ai():
    print("Testing crawl4ai package...")
    try:
        async with AsyncWebCrawler() as crawler:
            print("Successfully created AsyncWebCrawler instance.")
            result = await crawler.arun(url="https://example.com")
            if result.success:
                print("Successfully crawled example.com")
                print(f"HTML length: {len(result.html)} characters")
                print(f"First 100 characters: {result.html[:100]}...")
                return True
            else:
                print(f"Failed to crawl: {result.error_message}")
                return False
    except Exception as e:
        print(f"Error while testing crawl4ai: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(test_crawl4ai())
