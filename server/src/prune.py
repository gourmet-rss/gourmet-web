import asyncio
from src import constants
from src import database


async def prune_old_content():
  print(f"Pruning content older than {constants.MAX_CONTENT_AGE} days...")

  db = await database.get_db()
  try:
    count_query = f"""
        SELECT COUNT(*) as count
        FROM content
        WHERE date < CURRENT_DATE - INTERVAL '{constants.MAX_CONTENT_AGE} days'
        """
    result = await db.fetch_one(count_query)
    count = result["count"] if result else 0

    delete_query = f"""
        DELETE FROM content
        WHERE date < CURRENT_DATE - INTERVAL '{constants.MAX_CONTENT_AGE} days'
        """
    await db.execute(delete_query)

    print(f"Pruned {count} content items older than {constants.MAX_CONTENT_AGE} days")
    return count
  except Exception as e:
    print(f"Error pruning old content: {e}")
    return 0


async def prune_ingestion_logs():
  print("Pruning ingestion logs older than 24 hours...")

  db = await database.get_db()
  try:
    count_query = """
        SELECT COUNT(*) as count
        FROM ingestion_jobs
        WHERE start_time < CURRENT_TIMESTAMP - INTERVAL '24 hours'
        """
    result = await db.fetch_one(count_query)
    count = result["count"] if result else 0

    delete_query = """
        DELETE FROM ingestion_jobs
        WHERE start_time < CURRENT_TIMESTAMP - INTERVAL '24 hours'
        """
    await db.execute(delete_query)

    print(f"Pruned {count} ingestion logs older than 24 hours")
    return count
  except Exception as e:
    print(f"Error pruning ingestion logs: {e}")
    return 0


async def main():
  try:
    print("Starting database pruning operations...")

    content_count = await prune_old_content()
    logs_count = await prune_ingestion_logs()

    print(f"Pruning complete. Removed {content_count} content items and {logs_count} ingestion logs.")
  except Exception as e:
    print(f"Error during pruning operations: {e}")
  finally:
    await database.close_db()


if __name__ == "__main__":
  asyncio.run(main())
