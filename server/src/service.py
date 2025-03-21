import torch
import uuid
import numpy as np
from datetime import datetime
from src import database, util, constants
import sqlalchemy


#
#
#
async def get_recommendation_candidates(user_embedding: list, recommendation_ids: list[int] | None = None):
  """
  Get a list of recommendation candidates for a user
  """

  db = await database.get_db()

  # Find all content ids near the user embedding
  candidates = await db.fetch_all(
    f"""
        SELECT c.id, c.date, c.embedding <-> :user_embedding AS distance
        FROM content c
        LEFT JOIN user_content_ratings ucr ON c.id = ucr.content_id AND ucr.user_id = :user_id AND ucr.rating < 0
        WHERE c.date >= CURRENT_DATE - INTERVAL '{constants.MAX_CONTENT_AGE} days'
        AND c.id NOT IN (SELECT UNNEST(cast(:ignored_ids as int[])))
        AND ucr.id IS NULL
        AND c.embedding <-> :user_embedding < :max_distance
        ORDER BY c.embedding <-> :user_embedding
        LIMIT :limit
    """,
    {
      "user_embedding": util.list_to_string(user_embedding),
      "ignored_ids": recommendation_ids,
      "max_distance": constants.MAX_SEARCH_DISTANCE,
      "limit": 100,
    },
  )

  current_date = datetime.now().timestamp()

  # Adjust the distance by applying the age penalty
  for candidate in candidates:
    age_in_seconds = current_date - candidate.date.timestamp()
    age_in_hours = age_in_seconds / 3600
    candidate.distance += age_in_hours * constants.AGE_PENALTY_FACTOR

  # Sort the candidates by distance
  candidates.sort(key=lambda x: x.distance)

  if not candidates:
    raise Exception("No content found")

  return candidates


def rank_candidates(candidates: list):
  """
  Rank the candidates based on their distance and a random factor
  """

  for idx, candidate in enumerate(candidates):
    candidate.rating = len(candidates) / ((idx + 1) * np.random.random())

  candidates.sort(key=lambda x: x.rating)

  return candidates


async def get_recommendations(user_id: int, recommendation_ids: list[int] | None = None):
  """
  Get recommendations for user
  """

  db = await database.get_db()
  user = await db.fetch_one(database.users.select().where(database.users.c.id == user_id))

  candidates = await get_recommendation_candidates(user.embedding, recommendation_ids)
  ranked_candidates = rank_candidates(candidates)
  recommendation_ids = [candidate.id for candidate in ranked_candidates][: constants.NUM_RECOMMENDATIONS]

  # Join content with user_content_ratings to get user ratings
  content = await db.fetch_all(
    """
    SELECT
      c.id, c.content_type, c.title, c.url, c.description, c.source_id, c.date, c.media,
      s.url as source_url,
      COALESCE(ucr.rating, 0) as rating
    FROM content c
    LEFT JOIN user_content_ratings ucr ON c.id = ucr.content_id AND ucr.user_id = :user_id
    LEFT JOIN sources s ON c.source_id = s.id
    WHERE c.id IN (SELECT UNNEST(cast(:content_ids as int[])))
    """,
    {"user_id": user_id, "content_ids": recommendation_ids},
  )

  return content


#
#
#
async def update_user_embedding(user_id: int, updated_embedding: torch.Tensor):
  db = await database.get_db()
  await db.execute(database.users.update().where(database.users.c.id == user_id), {"embedding": updated_embedding})


async def update_user_content_rating(user_id: int, content_id: int, rating: float):
  db = await database.get_db()

  # First check if a rating already exists
  existing_rating = await db.fetch_one(
    database.user_content_ratings.select().where(
      (database.user_content_ratings.c.user_id == user_id) & (database.user_content_ratings.c.content_id == content_id)
    )
  )

  if existing_rating:
    # Update existing rating
    await db.execute(
      database.user_content_ratings.update().where(
        (database.user_content_ratings.c.user_id == user_id)
        & (database.user_content_ratings.c.content_id == content_id)
      ),
      {"rating": rating, "timestamp": sqlalchemy.func.now()},
    )
  else:
    # Insert new rating
    await db.execute(
      database.user_content_ratings.insert(), {"user_id": user_id, "content_id": content_id, "rating": rating}
    )


async def handle_feedback(user_id: int, content_id: int, rating: float):
  """
  Adjust user embedding based on feedback

  Args:
      user_id (int): ID of the user providing feedback
      content_id (int): ID of the content being rated
      rating (float): Rating value indicating user's feedback between -1 and 1
  """

  if rating > 1 or rating < -1:
    raise Exception("Rating must be between -1 and 1")

  db = await database.get_db()
  user = await db.fetch_one(database.users.select().where(database.users.c.id == user_id))
  content = await db.fetch_one(database.content.select().where(database.content.c.id == content_id))

  # Adjust the embedding based on the rating using exponential moving average (EMA)
  updated_embedding = constants.USER_ADJUST_FACTOR * content.embedding * rating + (
    (1 - constants.USER_ADJUST_FACTOR) * user.embedding
  )

  # Normalize the embedding to unit length
  norm = torch.linalg.vector_norm(torch.tensor(updated_embedding))
  if norm > 0:
    updated_embedding = updated_embedding / norm

  # Print the geometric length (norm) of the embedding
  print("Embedding norm: ", norm)
  print("Updated embedding norm: ", torch.linalg.vector_norm(torch.tensor(updated_embedding)))

  await update_user_embedding(user_id, updated_embedding)
  await update_user_content_rating(user_id, content_id, rating)


#
#
#
async def sign_up():
  user_id = uuid.uuid4()

  db = await database.get_db()

  user = await db.execute(database.users.insert(), {"id": user_id})

  return user


#
#
#
async def get_onboarding_content(existing_selected_content_ids: list):
  db = await database.get_db()

  sample_count = constants.SAMPLE_COUNT - len(existing_selected_content_ids)

  # Get a random sample of content ids
  sample_content_ids = await db.fetch_all(
    """
        SELECT id AS id
        FROM content
        WHERE embedding IS NOT NULL
        AND id NOT IN (SELECT UNNEST(cast(:existing_ids as int[])))
        ORDER BY RANDOM()
        LIMIT :sample_count
    """,
    {"existing_ids": existing_selected_content_ids, "sample_count": sample_count},
  )

  if len(sample_content_ids) == 0:
    raise Exception("No content found")

  existing_content = await db.fetch_all(
    database.content.select().where(database.content.c.id.in_(existing_selected_content_ids))
  )

  sample_content = await db.fetch_all(
    database.content.select().where(database.content.c.id.in_([x.id for x in sample_content_ids]))
  )

  return existing_content + sample_content


#
#
#
async def onboard(user_id: int, liked_content_ids: list):
  """
  Onboard a user by creating, then adjusting their embedding based on their feedback

  Args:
      user_id (int): ID of the user providing feedback
      liked_content_ids (list): List of content ids that the user liked
  """

  db = await database.get_db()

  liked_content = await db.fetch_all(database.content.select().where(database.content.c.id.in_(liked_content_ids)))

  # Create a user embedding based on the liked content
  liked_embeddings = torch.tensor(np.array([x.embedding for x in liked_content]))
  user_embedding = torch.mean(liked_embeddings, dim=0)

  # Save the user embedding to the database
  db = await database.get_db()
  await db.execute(
    database.users.update().where(database.users.c.id == user_id), {"embedding": user_embedding.tolist()}
  )
