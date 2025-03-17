import torch
import asyncio
import sentence_transformers
import feedparser
import datetime
import asyncpg

from src import database

model = sentence_transformers.SentenceTransformer("paraphrase-distilroberta-base-v1")


def get_content_embedding(content_item: feedparser.FeedParserDict) -> torch.Tensor:
  text = content_item.title + ": " + content_item.summary

  embedding = model.encode(text, normalize_embeddings=True)

  return embedding


async def process_content_item(source_id: int, content_item: feedparser.FeedParserDict, job_id: int):
  embedding = get_content_embedding(content_item)
  published_date = None
  if "published_parsed" in content_item:
    published_date = datetime.datetime(*content_item.published_parsed[:6])
  elif "updated_parsed" in content_item:
    published_date = datetime.datetime(*content_item.updated_parsed[:6])
  else:
    print(f"WARNING: No date found for {content_item.link}")
    published_date = datetime.datetime.now()

  # Extract image URL if available
  image_url = None
  image_text = None
  if "media_content" in content_item and content_item.media_content:
    for media in content_item.media_content:
      if "url" in media:
        image_url = media["url"]
        image_text = media.get("description", None)
        break
  elif "links" in content_item:
    for link in content_item.links:
      if link.get("type", "").startswith("image/"):
        image_url = link.get("href")
        image_text = link.get("title", None)
        break

  # Determine content type based on available information
  content_type = "article"  # Default type

  # Check for podcast/audio content
  if "enclosures" in content_item:
    for enclosure in content_item.enclosures:
      if enclosure.get("type", "").startswith("audio/"):
        content_type = "podcast"
        break

  # Check for video content
  if content_type == "article" and "media_content" in content_item:
    for media in content_item.media_content:
      if media.get("type", "").startswith("video/"):
        content_type = "video"
        break

  # Additional check in links for video/audio
  if content_type == "article" and "links" in content_item:
    for link in content_item.links:
      link_type = link.get("type", "")
      if link_type.startswith("video/"):
        content_type = "video"
        break
      elif link_type.startswith("audio/"):
        content_type = "podcast"
        break

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
        "image_url": image_url,
        "image_text": image_text,
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
    print(f"WARNING: Already processed {content_item.link}, skipping")
    return False


async def get_last_ingestion_date():
  """Get the start time of the last successful ingestion job"""
  db = await database.get_db()
  result = await db.fetch_one(
    """SELECT start_time
       FROM ingestion_jobs
       WHERE status = 'completed'
       ORDER BY start_time DESC
       LIMIT 1"""
  )
  return result["start_time"] if result else None


async def create_ingestion_job():
  """Create a new ingestion job and return its ID"""
  db = await database.get_db()
  result = await db.fetch_one(
    """INSERT INTO ingestion_jobs
       (start_time, status, items_processed, items_added)
       VALUES (:start_time, :status, :items_processed, :items_added)
       RETURNING id""",
    {"start_time": datetime.datetime.now(), "status": "running", "items_processed": 0, "items_added": 0},
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
      await process_content_item(feed_id, entry, job_id)
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
    job_id = await create_ingestion_job()
    print(f"Starting ingestion job {job_id}")
    last_ingestion_date = await get_last_ingestion_date()
    if last_ingestion_date:
      print(f"Only processing items newer than {last_ingestion_date}")
    db = await database.get_db()
    sources = await db.fetch_all(database.sources.select())
    total_processed = 0
    for source in sources:
      try:
        processed = await feed_ingestion(source.id, source.url, job_id, last_ingestion_date)
        total_processed += processed
      except Exception as e:
        print(f"Error processing source {source.url}: {e}")
    await complete_ingestion_job(job_id)
    print(f"Completed ingestion job {job_id}. Processed {total_processed} items.")
  except Exception as e:
    print(f"Error in ingestion pipeline: {e}")
    await complete_ingestion_job(job_id, success=False, error_message=str(e))
  finally:
    await database.close_db()


if __name__ == "__main__":
  asyncio.run(main())
