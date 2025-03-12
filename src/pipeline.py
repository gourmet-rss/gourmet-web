import torch
import asyncio
import sentence_transformers
import feedparser
import datetime
import asyncpg

from src import database

model = sentence_transformers.SentenceTransformer("paraphrase-MiniLM-L6-v2")


def get_content_embedding(content_item) -> torch.Tensor:
  text = content_item.title + ": " + content_item.summary

  embedding = model.encode(text, normalize_embeddings=True)

  return embedding


async def process_content_item(source_id: int, content_item: feedparser.FeedParserDict):
  embedding = get_content_embedding(content_item)
  published_date = None
  try:
    published_date = datetime.datetime(*content_item.published_parsed[:6])
  except Exception as e:
    published_date = datetime.datetime(*content_item.updated_parsed[:6])

  db = await database.get_db()
  try:
    await db.execute(
      database.content.insert(),
      {
        "title": content_item.title,
        "url": content_item.link,
        "description": content_item.summary,
        "source_id": source_id,
        "date": published_date,
        "embedding": embedding.tolist(),
      },
    )
  except asyncpg.exceptions.UniqueViolationError as e:
    print(f"WARNING: Already processed {content_item.link}, skipping")


async def feed_ingestion(feed_id: int, feed_url: str):
  try:
    print("Ingesting feed", feed_url)
    feed = feedparser.parse(feed_url)
    for entry in feed.entries:
      await process_content_item(feed_id, entry)
  finally:
    await database.close_db()


async def main():
  db = await database.get_db()

  sources = await db.fetch_all(database.sources.select())

  for source in sources:
    await feed_ingestion(source.id, source.url)


if __name__ == "__main__":
  asyncio.run(main())
