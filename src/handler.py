import torch
import uuid
import numpy as np
import datetime
from src import database, util, constants


async def get_a_recommendation_id(user_embedding: list, recommendation_ids: list):
  """
  Get a single recommendation id for a user
  """

  db = await database.get_db()

  # Create a small adjustment to the user embedding and use it to find a new recommendation
  max_change_proportion = 0.0001
  random_delta = (2 * max_change_proportion * torch.rand(constants.EMBED_DIM)) - 1
  new_embedding = user_embedding + random_delta

  # Find the closest content to the new embedding
  results = await db.fetch_all(
    """
        SELECT id, embedding <-> :user_embedding as distance
        FROM content
        WHERE date >= CURRENT_DATE - INTERVAL :interval
        AND id NOT IN :ignored_ids
        ORDER BY embedding <-> :user_embedding
        LIMIT :limit
    """,
    {
      "user_embedding": util.list_to_string(new_embedding),
      "limit": 50,
      "interval": "7 days",
      "ignored_ids": recommendation_ids,
    },
  )

  current_date = datetime.now()

  # Adjust the distance by applying the age penalty
  chosen_result_id = None
  min_distance = float("inf")
  for result in results:
    age_in_days = (current_date - result.date).days
    adjusted_distance = result.distance + (age_in_days * constants.AGE_PENALTY_FACTOR)

    if adjusted_distance < min_distance:
      min_distance = adjusted_distance
      chosen_result_id = result.id

  if not chosen_result_id:
    raise Exception("No content found")

  return chosen_result_id


async def get_recommendations(user_id: int):
  """
  Get recommendations for user
  """

  db = await database.get_db()
  user = await db.fetch_one(database.users.select().where(database.users.c.id == user_id))

  recommendation_ids = []

  for idx in range(constants.NUM_RECOMMENDATIONS):
    recommendation_id = await get_a_recommendation_id(user.embedding, recommendation_ids)
    recommendation_ids.append(recommendation_id)

  content = await db.fetch_all(database.content.select().where(database.content.c.id.in_(recommendation_ids)))

  return content


async def handle_feedback(user_id: int, content_id: int, rating: int):
  db = await database.get_db()
  user = await db.fetch_one(database.users.select().where(database.users.c.id == user_id))
  content = await db.fetch_one(database.content.select().where(database.content.c.id == content_id))

  user_to_content_delta = user.embedding - content.embedding
  adjust_delta = user_to_content_delta * rating * constants.USER_ADJUST_FACTOR
  updated_embedding = user.embedding + adjust_delta

  await db.execute(database.users.update(database.users.c.id == user_id), {"embedding": updated_embedding.tolist()})


async def sign_up():
  user_id = uuid.uuid4()

  db = await database.get_db()

  await db.execute(database.users.insert(), {"id": user_id})

  # Get a random sample of content ids
  sample_content_ids = await db.fetch_all(f"""
        SELECT MIN(id) AS id
        FROM content
        WHERE embedding IS NOT NULL
        GROUP BY source_id
        ORDER BY RANDOM()
        LIMIT {constants.SAMPLE_COUNT}
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
