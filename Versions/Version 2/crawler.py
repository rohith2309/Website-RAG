from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.content_filter_strategy import PruningContentFilter
from langchain_core.documents import Document
import json
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)



async def crawl_website(
    urls: list[str],

):
    

    run_config = CrawlerRunConfig(
    markdown_generator=DefaultMarkdownGenerator(
        content_filter=PruningContentFilter(
            threshold=0.45,
            min_word_threshold=30,
            threshold_type="dynamic",
        ),
        
        options={"ignore_images": True, "ignore_videos": True,"ignore_links": True,"skip_internal_links": True},
        ),
        excluded_tags=["header", "footer", "nav", "aside", "form"]

    )

    kb_dir = Path("./KB")
    kb_dir.mkdir(exist_ok=True)

    crawl_file = kb_dir / "crawl_results.jsonl"

    docs = []
    results=[]

    async with AsyncWebCrawler() as crawler:
        for url in urls:
            result = await crawler.arun(
                        url=url,
                        config=run_config,
                        )
            results.append(result)
        logging.info(f"Finished crawling {len(results)} URLs")

        with open(crawl_file, "w", encoding="utf-8") as f:

            for i, result in enumerate(results):

                if not result.success:
                    continue

                # Store useful information for inspection
                record = {
                    "index": i,
                    "url": result.url,
                    "title": getattr(result, "title", ""),
                    "word_count": len(
                        result.markdown.split()
                    ) if result.markdown else 0,
                    "content": result.markdown or result.markdown.fit_markdown or result.markdown.raw_markdown or "",
                }

                f.write(
                    json.dumps(
                        record,
                        ensure_ascii=False
                    ) + "\n"
                )

                docs.append(
                    Document(
                        page_content=result.markdown or "",
                        metadata={
                            "url": result.url,
                            "title": getattr(
                                result,
                                "title",
                                ""
                            ),
                        }
                    )
                )

    print(f"Saved crawl results to: {crawl_file}")
    print(f"Pages crawled: {len(docs)}")    


    return docs