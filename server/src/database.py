from databases import Database
import sqlalchemy
from sqlalchemy.dialects import postgresql
import asyncio
from pgvector.sqlalchemy import Vector
import json
import os
from jsmin import jsmin
from src import constants

dirname = os.path.dirname(__file__)

# Create a single global pool that can be reused
_pool = None

DATABASE_URL = os.getenv("DATABASE_URL")


async def get_db():
  global _pool
  if _pool is None:
    _pool = Database(DATABASE_URL or "postgresql+asyncpg://postgres:password@localhost:5433")
    await _pool.connect()
  return _pool


# Add a function to close the pool when done
async def close_db():
  global _pool
  if _pool is not None:
    await _pool.disconnect()
    _pool = None


metadata = sqlalchemy.MetaData()
dialect = postgresql.dialect()

users = sqlalchemy.Table(
  "users",
  metadata,
  sqlalchemy.Column("id", sqlalchemy.String, primary_key=True),
  sqlalchemy.Column("embedding", Vector(constants.EMBED_DIM)),
)

sources = sqlalchemy.Table(
  "sources",
  metadata,
  sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
  sqlalchemy.Column("url", sqlalchemy.String, unique=True),
  sqlalchemy.Column("source_type", sqlalchemy.String),
)

content = sqlalchemy.Table(
  "content",
  metadata,
  sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
  sqlalchemy.Column("content_type", sqlalchemy.String),
  sqlalchemy.Column("title", sqlalchemy.String),
  sqlalchemy.Column("url", sqlalchemy.String, unique=True),
  sqlalchemy.Column("description", sqlalchemy.String),
  sqlalchemy.Column("source_id", sqlalchemy.Integer),
  sqlalchemy.Column("date", sqlalchemy.DateTime(timezone=True)),
  sqlalchemy.Column("embedding", Vector(constants.EMBED_DIM)),
  sqlalchemy.Column("media", sqlalchemy.JSON, nullable=True),
)

user_content_ratings = sqlalchemy.Table(
  "user_content_ratings",
  metadata,
  sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
  sqlalchemy.Column("user_id", sqlalchemy.String, sqlalchemy.ForeignKey("users.id")),
  sqlalchemy.Column("content_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("content.id")),
  # Can store ratings from -1 to 1 with 0.001 precision
  sqlalchemy.Column("rating", sqlalchemy.Numeric(precision=4, scale=3)),
  sqlalchemy.Column("timestamp", sqlalchemy.DateTime(timezone=True), server_default=sqlalchemy.func.now()),
  sqlalchemy.UniqueConstraint("user_id", "content_id", name="uq_user_content_rating"),
)

ingestion_jobs = sqlalchemy.Table(
  "ingestion_jobs",
  metadata,
  sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
  sqlalchemy.Column("source_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("sources.id")),
  sqlalchemy.Column("start_time", sqlalchemy.DateTime(timezone=True)),
  sqlalchemy.Column("end_time", sqlalchemy.DateTime(timezone=True)),
  sqlalchemy.Column("status", sqlalchemy.String),  # 'running', 'completed', 'failed'
  sqlalchemy.Column("items_processed", sqlalchemy.Integer),
  sqlalchemy.Column("items_added", sqlalchemy.Integer),
  sqlalchemy.Column("error_message", sqlalchemy.String, nullable=True),
)

# flavours are separate sessions the user can access which have a different embedding
user_flavours = sqlalchemy.Table(
  "user_flavours",
  metadata,
  sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
  sqlalchemy.Column("nickname", sqlalchemy.String, nullable=True),
  sqlalchemy.Column("user_id", sqlalchemy.String, sqlalchemy.ForeignKey("users.id")),
  sqlalchemy.Column("embedding", Vector(constants.EMBED_DIM)),
  sqlalchemy.Column("created_at", sqlalchemy.DateTime(timezone=True), server_default=sqlalchemy.func.now()),
)


constants_table = sqlalchemy.Table(
  "constants",
  metadata,
  sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
  sqlalchemy.Column("name", sqlalchemy.String, unique=True),
  sqlalchemy.Column("value", sqlalchemy.String),
  sqlalchemy.Column("description", sqlalchemy.String, nullable=True),
  sqlalchemy.Column("created_at", sqlalchemy.DateTime(timezone=True), server_default=sqlalchemy.func.now()),
  sqlalchemy.Column(
    "updated_at",
    sqlalchemy.DateTime(timezone=True),
    server_default=sqlalchemy.func.now(),
    onupdate=sqlalchemy.func.now(),
  ),
)


async def seed() -> None:
  db = await get_db()

  with open(os.path.join(dirname, "../feeds.jsonc"), "r") as f:
    data = json.loads(jsmin(f.read()))

  for category, urls in data.items():
    if urls:
      for url in urls:
        try:
          # Use ON CONFLICT to avoid duplicates (since url is PRIMARY KEY)
          insert_query = """
                  INSERT INTO sources (url, source_type)
                  VALUES (:url, :source_type)
                  ON CONFLICT (url) DO NOTHING;
                  """
          await db.execute(query=insert_query, values={"url": url, "source_type": "rss"})
          print(f"Inserted {url}")
        except Exception as e:
          print(f"Error inserting {url}: {e}")

  # Insert constants into the constants table
  for name, details in constants.DB_CONSTANTS.items():
    try:
      insert_query = """
              INSERT INTO constants (name, value, description)
              VALUES (:name, :value, :description)
              ON CONFLICT (name) DO UPDATE SET
                  value = EXCLUDED.value,
                  description = EXCLUDED.description,
                  updated_at = NOW();
              """
      await db.execute(
        query=insert_query, values={"name": name, "value": str(details["value"]), "description": details["description"]}
      )
      print(f"Inserted {name}")
    except Exception as e:
      print(f"Error inserting constant {name}: {e}")


if __name__ == "__main__":
  print("Seeding database...")
  asyncio.run(seed())
  print("> Done")
