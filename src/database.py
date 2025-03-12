from databases import Database
import sqlalchemy
from sqlalchemy.dialects import postgresql
import asyncio
from pgvector.sqlalchemy import Vector
import json
import os
from jsmin import jsmin

dirname = os.path.dirname(__file__)


async def get_db():
  client = Database("postgresql://postgres:password@localhost:5432")
  await client.connect()
  return client


metadata = sqlalchemy.MetaData()
dialect = postgresql.dialect()

users = sqlalchemy.Table(
  "users",
  metadata,
  sqlalchemy.Column("id", sqlalchemy.UUID, primary_key=True),
  sqlalchemy.Column("embedding", Vector(512)),
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
  sqlalchemy.Column("title", sqlalchemy.String),
  sqlalchemy.Column("url", sqlalchemy.String),
  sqlalchemy.Column("description", sqlalchemy.String),
  sqlalchemy.Column("source_id", sqlalchemy.Integer),
  sqlalchemy.Column("embedding", Vector(512)),
)


async def migrate():
  db = await get_db()
  for table in metadata.tables.values():
    try:
      schema = sqlalchemy.schema.DropTable(table)
      query = str(schema.compile(dialect=dialect))
      await db.execute(query=query)
    except:
      pass
    schema = sqlalchemy.schema.CreateTable(table, if_not_exists=False)
    query = str(schema.compile(dialect=dialect))
    await db.execute(query=query)

  with open(os.path.join(dirname, "../feeds.jsonc"), "r") as f:
    data = json.loads(jsmin(f.read()))

  for category, urls in data.items():
    if urls:
      first_url = urls[0]
      try:
        # Use ON CONFLICT to avoid duplicates (since url is PRIMARY KEY)
        insert_query = """
                INSERT INTO sources (url, source_type)
                VALUES (:url, :source_type)
                ON CONFLICT (url) DO NOTHING;
                """
        await db.execute(query=insert_query, values={"url": first_url, "source_type": "rss"})
      except Exception as e:
        print(f"Error inserting {first_url}: {e}")


if __name__ == "__main__":
  print("Running migrations...")
  asyncio.run(migrate())
  print("> Done")
