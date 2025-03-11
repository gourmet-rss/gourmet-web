import torch
import uuid
import numpy as np
from src import database, util


async def get_recommendations(user_id: int):
  db = await database.get_db()
  user = await db.fetch_one(database.users.select().where(database.users.c.id == user_id))

  # TODO - randomnly push the query embedding around within a radius to add a sort of "temperature" to results
  results = await db.fetch_all(
    """
        SELECT id, embedding <-> :user_embedding as distance
        FROM content
        ORDER BY embedding <-> :user_embedding
        LIMIT :limit
    """,
    {"user_embedding": util.list_to_string(user.embedding), "limit": 5},
  )

  content_ids = tuple([x.id for x in results])

  if len(content_ids) == 0:
    raise Exception("No content found")

  content = await db.fetch_all(database.content.select().where(database.content.c.id.in_(content_ids)))

  return content


async def sign_up():
  user_id = uuid.uuid4()

  db = await database.get_db()

  await db.execute(database.users.insert(), {"id": user_id})

  sample_count = 100

  sample_content_ids = await db.fetch_all(f"""
        SELECT MIN(id) AS id
        FROM content
        WHERE embedding IS NOT NULL
        GROUP BY source_id
        ORDER BY RANDOM()
        LIMIT {sample_count}
    """)

  if len(sample_content_ids) == 0:
    raise Exception("No content found")

  sample_content_ids = tuple([x.id for x in sample_content_ids])

  sample_content = await db.fetch_all(database.content.select().where(database.content.c.id.in_(sample_content_ids)))

  print(f"Signed up as {user_id}")

  return user_id, sample_content


async def onboard(user_id: int, selected_content: list):
  content_embeddings = torch.tensor(np.array([x.embedding for x in selected_content]))
  mean_embedding = torch.mean(content_embeddings, dim=0)

  db = await database.get_db()

  await db.execute(
    database.users.update().where(database.users.c.id == user_id), {"embedding": mean_embedding.tolist()}
  )


async def main():
  user_id = input("What is your user id? Leave blank to sign up.")

  if not user_id:
    user_id, sample_content = await sign_up()

    print("Here are some posts you may be interested in")
    for i, item in enumerate(sample_content):
      print(f"{i + 1}) {item['title']}")

    res = input("Choose some posts by entering their numbers (separated by commas), then press enter:\n")

    content_indices = [int(x) for x in res.split(",")]

    selected_content = [sample_content[i - 1] for i in content_indices]

    await onboard(user_id, selected_content)

  recs = await get_recommendations(user_id)

  print(f"Here are some recommended posts for you:\n{util.list_to_string([rec['title'] for rec in recs])}")


if __name__ == "__main__":
  import asyncio

  asyncio.run(main())
