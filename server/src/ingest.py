import os
import torch
import asyncio
import feedparser
import datetime
import asyncpg
import ollama
import bs4
import bleach
from typing import Literal

from src import database

ollama_client = ollama.Client(host=os.getenv("OLLAMA_HOST", "http://localhost:11435"))


#
#
#
def get_content_embedding(feed_item: feedparser.FeedParserDict) -> torch.Tensor:
  text = feed_item.title + ": " + feed_item.summary

  res = ollama_client.embed(model="bge-m3", input=text)

  embedding = torch.tensor(res.embeddings[0])

  return embedding


def clean_description(description: str) -> str:
  # Allow only safe HTML tags (e.g., <p>, <a>, <img>)
  allowed_tags = ["p", "a", "br", "ul", "li", "strong", "em"]
  cleaned = bleach.clean(description, tags=allowed_tags, strip=True)

  # Extract text-only alternative
  text_only = bleach.clean(description, strip=True)

  return cleaned, text_only


def extract_media(feed_item: feedparser.FeedParserDict) -> list[dict[str, str]]:
  media = []

  # 1. Check RSS enclosures (podcasts/images)
  for enclosure in getattr(feed_item, "enclosures", []):
    media.append(
      {
        "type": enclosure.type.split("/")[0],  # 'image', 'audio', etc.
        "url": enclosure.href,
        "source": "enclosure",
      }
    )

  # 2. Check Media RSS
  if hasattr(feed_item, "media_content"):
    for mc in feed_item.media_content:
      media.append({"type": mc.get("medium", mc.type.split("/")[0]), "url": mc["url"], "source": "media_rss"})

  # 3. Scrape HTML description for embedded media
  soup = bs4.BeautifulSoup(feed_item.description, "html.parser")
  for img in soup.find_all("img"):
    media.append({"type": "image", "url": img.get("src"), "source": "html_embed"})

  return media


ContentType = Literal["audio", "video", "article", "unknown"]


def detect_content_type(feed_item: feedparser.FeedParserDict) -> ContentType:
  # Initialize type counters
  type_counts = {"audio": 0, "video": 0, "article": 0}

  # Priority 1: Check RSS/Media-RSS explicit tags
  if hasattr(feed_item, "media_medium"):
    if feed_item.media_medium == "audio":
      type_counts["audio"] += 2
    elif feed_item.media_medium == "video":
      type_counts["video"] += 2

  # Priority 2: Analyze enclosures
  for enc in getattr(feed_item, "enclosures", []):
    if enc.type.startswith("audio/"):
      type_counts["audio"] += 1
      break  # Only count once per type
    elif enc.type.startswith("video/"):
      type_counts["video"] += 1
      break

  # Priority 3: Heuristics (title/description/category)
  text = (feed_item.title + " " + feed_item.description).lower()
  if "podcast" in text or "episode" in text:
    type_counts["audio"] += 1
  elif "video" in text or "watch" in text:
    type_counts["video"] += 1

  # Determine final type based on majority
  max_count = max(type_counts.values())
  if max_count >= 2:
    return max(type_counts, key=type_counts.get)

  # Default to article if no clear majority
  return "article" if not getattr(feed_item, "enclosures", []) else "unknown"


#
#
#
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

  media = extract_media(feed_item)
  content_type = detect_content_type(feed_item)
  summary_html, _ = clean_description(feed_item.summary) if hasattr(feed_item, "summary") else ("", "")

  db = await database.get_db()
  try:
    await db.execute(
      database.content.insert(),
      {
        "title": feed_item.title,
        "url": feed_item.link,
        "description": summary_html,
        "source_id": source_id,
        "date": published_date,
        "embedding": embedding.tolist(),
        "media": media,
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
    print(f"WARNING: Already processed {feed_item.title} source_id: {source_id}, skipping")
    return False


#
#
#
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


#
#
#
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


#
#
#
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


#
#
#
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
