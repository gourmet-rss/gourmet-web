import os
import torch
import asyncio
import feedparser
import datetime
import asyncpg
import html
import ollama

from src import database

print("host", os.getenv("OLLAMA_HOST", "http://localhost:11435"))
ollama_client = ollama.Client(host=os.getenv("OLLAMA_HOST", "http://localhost:11435"))


def get_content_embedding(feed_item: feedparser.FeedParserDict) -> torch.Tensor:
  text = feed_item.title + ": " + feed_item.summary

  res = ollama_client.embed(model="bge-m3", input=text)

  embedding = torch.tensor(res.embeddings[0])

  return embedding


async def process_feed_item(source_id: int, feed_item: feedparser.FeedParserDict, job_id: int):
  embedding = get_content_embedding(feed_item)
  published_date = None
  if "published_parsed" in feed_item:
    published_date = datetime.datetime(*feed_item.published_parsed[:6])
  elif "updated_parsed" in feed_item:
    published_date = datetime.datetime(*feed_item.updated_parsed[:6])
  else:
    print(f"WARNING: No date found for {feed_item.link}")
    published_date = datetime.datetime.now()

  # Determine content type based on available information
  content_type = "article"  # Default type

  # Check for podcast/audio content
  if "enclosures" in feed_item:
    for enclosure in feed_item.enclosures:
      if enclosure.get("type", "").startswith("audio/"):
        content_type = "audio"
        break

  # Check for video content
  if content_type == "article" and "media_content" in feed_item:
    for media in feed_item.media_content:
      if media.get("type", "").startswith("video/"):
        content_type = "video"
        break

  # Additional check in links for video/audio
  if content_type == "article" and "links" in feed_item:
    for link in feed_item.links:
      link_type = link.get("type", "")
      if link_type.startswith("video/"):
        content_type = "video"
        break
      elif link_type.startswith("audio/"):
        content_type = "audio"
        break

  # Sanitize text content
  summary = html.escape(feed_item.summary) if hasattr(feed_item, "summary") else ""

  db = await database.get_db()
  try:
    await db.execute(
      database.content.insert(),
      {
        "title": feed_item.title,
        "url": feed_item.link,
        "description": summary,
        "source_id": source_id,
        "date": published_date,
        "embedding": embedding.tolist(),
        "media": feed_item.get("media_content", []),
        "content_type": content_type,
      },
    )
    await db.execute(
      """UPDATE ingestion_jobs
         SET items_added = items_added + 1
         WHERE id = :job_id""",
      {"job_id": job_id},
    )
    return True
  except asyncpg.exceptions.UniqueViolationError:
    print(f"WARNING: Already processed {link}, skipping")
    return False


async def get_last_ingestion_date(source_id: int):
  """Get the start time of the last successful ingestion job for a specific source"""
  db = await database.get_db()
  result = await db.fetch_one(
    """SELECT start_time
       FROM ingestion_jobs
       WHERE status = 'completed' AND source_id = :source_id
       ORDER BY start_time DESC
       LIMIT 1""",
    {"source_id": source_id},
  )
  return result["start_time"] if result else None


async def create_ingestion_job(source_id: int):
  """Create a new ingestion job and return its ID"""
  db = await database.get_db()
  result = await db.fetch_one(
    """INSERT INTO ingestion_jobs
       (source_id, start_time, status, items_processed, items_added)
       VALUES (:source_id, :start_time, :status, :items_processed, :items_added)
       RETURNING id""",
    {
      "source_id": source_id,
      "start_time": datetime.datetime.now(),
      "status": "running",
      "items_processed": 0,
      "items_added": 0,
    },
  )
  return result["id"]


async def complete_ingestion_job(job_id: int, success: bool = True, error_message: str = None):
  """Mark an ingestion job as completed or failed"""
  db = await database.get_db()
  status = "completed" if success else "failed"
  await db.execute(
    """UPDATE ingestion_jobs
       SET end_time = :end_time, status = :status, error_message = :error_message
       WHERE id = :job_id""",
    {"end_time": datetime.datetime.now(), "status": status, "error_message": error_message, "job_id": job_id},
  )


async def feed_ingestion(feed_id: int, feed_url: str, job_id: int, last_ingestion_date: datetime.datetime = None):
  try:
    print(f"Ingesting feed {feed_url}")
    feed = feedparser.parse(feed_url)
    items_processed = 0
    for entry in feed.entries:
      entry_date = None
      if "published_parsed" in entry:
        entry_date = datetime.datetime(*entry.published_parsed[:6], tzinfo=datetime.timezone.utc)
      elif "updated_parsed" in entry:
        entry_date = datetime.datetime(*entry.updated_parsed[:6], tzinfo=datetime.timezone.utc)
      if last_ingestion_date and entry_date and entry_date <= last_ingestion_date:
        print(f"Skipping {entry.link} - older than last ingestion")
        continue
      await process_feed_item(feed_id, entry, job_id)
      items_processed += 1
    db = await database.get_db()
    await db.execute(
      """UPDATE ingestion_jobs
         SET items_processed = items_processed + :count
         WHERE id = :job_id""",
      {"count": items_processed, "job_id": job_id},
    )
    return items_processed
  except Exception as e:
    print(f"Error ingesting feed {feed_url}: {e}")
    raise


async def main():
  try:
    print("Starting ingestion pipeline")
    db = await database.get_db()
    sources = await db.fetch_all(database.sources.select())
    total_processed = 0
    for source in sources:
      try:
        job_id = await create_ingestion_job(source.id)
        print(f"Starting ingestion job {job_id} for source {source.url}")
        last_ingestion_date = await get_last_ingestion_date(source.id)
        if last_ingestion_date:
          print(f"Only processing items newer than {last_ingestion_date}")
        processed = await feed_ingestion(source.id, source.url, job_id, last_ingestion_date)
        total_processed += processed
        await complete_ingestion_job(job_id, success=True)
      except Exception as e:
        print(f"Error processing source {source.url}: {e}")
        await complete_ingestion_job(job_id, success=False, error_message=str(e))
    print(f"Completed ingestion pipeline. Processed {total_processed} items.")
  except Exception as e:
    print(f"Error in ingestion pipeline: {e}")
  finally:
    await database.close_db()


if __name__ == "__main__":
  asyncio.run(main())
