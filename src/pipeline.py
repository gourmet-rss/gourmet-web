from src import classes
from src import database
import torch
import asyncio
from datetime import datetime


def get_content_embedding(content_item: classes.ContentItem) -> torch.Tensor:
  embedding = torch.zeros(512)

  embedding = torch.nn.functional.normalize(embedding, p=2, dim=-1)

  return embedding


async def process_content_item(content_item: classes.ContentItem):
  embedding = get_content_embedding(content_item)

  db = await database.get_db()
  await db.execute(
    database.content.insert(),
    {
      "title": content_item.title,
      "url": content_item.url,
      "description": content_item.description,
      "source_id": content_item.source_id,
      "embedding": embedding.tolist(),
    },
  )


if __name__ == "__main__":
  item1 = classes.ContentItem(
    title="Content Item 1",
    url="https://example.com/doc1",
    description="Description 1",
    date=datetime.now(),
    source_id=1,
    embedding=None,
  )

  asyncio.run(process_content_item(item1))
