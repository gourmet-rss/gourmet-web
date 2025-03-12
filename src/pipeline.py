import torch
import asyncio
import sentence_transformers
import feedparser
import datetime

from src import classes
from src import database

model = sentence_transformers.SentenceTransformer("paraphrase-MiniLM-L6-v2")


def get_content_embedding(content_item: classes.ContentItem) -> torch.Tensor:
  text = content_item.title + ": " + content_item.summary

  embedding = model.encode(text, normalize_embeddings=True)

  # print(embedding.tolist())
  # print(len(embedding))
  # print(type(embedding))
  # print("\n")

  return embedding


async def process_content_item(content_item: classes.ContentItem):
  embedding = get_content_embedding(content_item)
  published_date = datetime.datetime(*content_item.published_parsed[:6])

  db = await database.get_db()
  await db.execute(
    database.content.insert(),
    {
      "title": content_item.title,
      "url": content_item.link,
      "description": content_item.summary,
      "source_id": 1,
      "date": published_date,
      "embedding": embedding.tolist(),
    },
  )


async def feed_ingestion(feed_url: str):
  # print("\nFEED KEYS:", feed.keys())
  try:
    feed = feedparser.parse(feed_url)
    for entry in feed.entries:
      await process_content_item(entry)
  finally:
    await database.close_db()


if __name__ == "__main__":
  asyncio.run(
    feed_ingestion("https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"),
  )
