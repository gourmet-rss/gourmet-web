from databases import Database
import sqlalchemy
from sqlalchemy.dialects import postgresql
import asyncio
from pgvector.sqlalchemy import Vector


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

documents = sqlalchemy.Table(
  "documents",
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
    schema = sqlalchemy.schema.DropTable(table)
    query = str(schema.compile(dialect=dialect))
    await db.execute(query=query)
    schema = sqlalchemy.schema.CreateTable(table, if_not_exists=False)
    query = str(schema.compile(dialect=dialect))
    await db.execute(query=query)


if __name__ == "__main__":
  print("Running migrations...")
  asyncio.run(migrate())
  print("> Done")
