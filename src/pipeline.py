from src import classes
from src import database
import torch
import asyncio
from datetime import datetime


def get_document_embedding(document: classes.Document) -> torch.Tensor:
  embedding = torch.zeros(512)

  embedding = torch.nn.functional.normalize(embedding, p=2, dim=-1)

  return embedding


async def process_document(document: classes.Document):
  embedding = get_document_embedding(document)

  db = await database.get_db()
  await db.execute(
    database.documents.insert(),
    {
      "title": document.title,
      "url": document.url,
      "description": document.description,
      "source_id": document.source_id,
      "embedding": embedding.tolist(),
    },
  )


if __name__ == "__main__":
  doc1 = classes.Document(
    title="Document 1",
    url="https://example.com/doc1",
    description="Description 1",
    date=datetime.now(),
    source_id=1,
    embedding=None,
  )

  asyncio.run(process_document(doc1))
