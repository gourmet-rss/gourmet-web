import torch
import uuid
import numpy as np
from datetime import datetime
from src import database, util, constants


async def get_a_recommendation_id(user_embedding: list, recommendation_ids: list):
  """
  Get a single recommendation id for a user
  """

  db = await database.get_db()

  # Create a small adjustment to the user embedding and use it to find a new recommendation
  max_change_proportion = 0.0001
  random_delta = (2 * max_change_proportion * torch.rand(constants.EMBED_DIM)) - 1
  new_embedding = torch.tensor(user_embedding) + random_delta

  if len(recommendation_ids) == 0:
    # Add recommendation id to avoid syntax error if list empty
    recommendation_ids = [0]

  # Find the closest content to the new embedding
  results = await db.fetch_all(
    f"""
        SELECT id, date, embedding <-> :user_embedding AS distance
        FROM content
        WHERE date >= CURRENT_DATE - INTERVAL '{constants.MAX_CONTENT_AGE} days'
        AND id <> ANY(:ignored_ids)
        ORDER BY embedding <-> :user_embedding
        LIMIT :limit
    """,
    {"user_embedding": util.list_to_string(new_embedding.tolist()), "limit": 50, "ignored_ids": recommendation_ids},
  )

  current_date = datetime.now()

  # Adjust the distance by applying the age penalty
  chosen_result_id = None
  min_distance = float("inf")
  for result in results:
    age_in_seconds = current_date.timestamp() - result.date.timestamp()
    age_in_hours = age_in_seconds / 3600
    adjusted_distance = result.distance + (age_in_hours * constants.AGE_PENALTY_FACTOR)

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


async def handle_feedback(user_id: int, content_id: int, rating: float):
  """
  Adjust user embedding based on feedback

  Args:
      user_id (int): ID of the user providing feedback
      content_id (int): ID of the content being rated
      rating (float): Rating value indicating user's feedback between -1 and 1
  """

  db = await database.get_db()
  user = await db.fetch_one(database.users.select().where(database.users.c.id == user_id))
  content = await db.fetch_one(database.content.select().where(database.content.c.id == content_id))

  # Adjust the embedding based on the rating using exponential moving average (EMA)
  updated_embedding = (
    constants.USER_ADJUST_FACTOR * content.embedding * rating + (1 - constants.USER_ADJUST_FACTOR) * user.embedding
  )

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
  db = await database.get_db()
  users = await db.fetch_all(database.users.select())

  if len(users) > 0:
    print("Sign in:")
    for i, item in enumerate(users):
      print(f"{i + 1}) {item['id']}")
    selected_idx = input("Select the option number associated with your user ID, or leave blank to sign up: ")
    if selected_idx:
      user_id = users[int(selected_idx) - 1]["id"]
    else:
      user_id = None
  else:
    print("Signing up...")
    user_id = None

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
