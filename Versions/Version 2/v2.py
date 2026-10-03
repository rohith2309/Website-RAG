
import asyncio
import os
from dotenv import load_dotenv

import asyncio
import boto3
from crawl4ai import AsyncWebCrawler,CrawlerRunConfig
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from crawl4ai.deep_crawling.filters import (
    FilterChain,
    URLPatternFilter
)
from langchain_core.documents import Document

import asyncio
from crawl4ai import AsyncWebCrawler, AdaptiveCrawler, AdaptiveConfig,BrowserConfig

async def crawler(url: str, descriptive_query:str):
    # Configure adaptive crawling
    config = AdaptiveConfig(
        confidence_threshold=0.75,
        max_pages=15,
        save_state=True,
        state_path="my_crawl.json"
    )

    async with AsyncWebCrawler() as crawler:
        adaptive = AdaptiveCrawler(crawler, config)

        # Start crawling
        state = await adaptive.digest(
            start_url=url,
            query=descriptive_query
        )

        # Check results
        print(f"Confidence achieved: {adaptive.confidence:.0%}")
        adaptive.print_stats()

        # Get most relevant pages
        for page in adaptive.get_relevant_content(top_k=3):
            print(f"- {page['url']} (score: {page['score']:.2f})")

        # Export for later use
        adaptive.export_knowledge_base("./KB/auth_knowledge.jsonl")

if __name__ == "__main__":
    asyncio.run(crawler("https://docs.crawl4ai.com/", "How to configure adaptive crawling with a confidence threshold and export the knowledge base?"))
